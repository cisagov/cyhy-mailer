#!/usr/bin/env python3

"""cyhy-mailer: A tool for mailing out reports.

cyhy-mailer can send out Cyber Hygiene and BOD 18-01 reports, as well
as Cyber Hygiene notifications and the Cyber Exposure scorecard.

Usage:
  cyhy-mailer (bod1801|cybex|cyhy|notification)... [--cyhy-report-dir=DIRECTORY] [--tmail-report-dir=DIRECTORY] [--https-report-dir=DIRECTORY] [--cybex-scorecard-dir=DIRECTORY] [--cyhy-notification-dir=DIRECTORY] [--db-creds-file=FILENAME] [--batch-size=SIZE] [--summary-to=EMAILS] [--debug] [--dry-run]
  cyhy-mailer (-h | --help)

Options:
  -h --help                         Show this message.
  --cyhy-report-dir=DIRECTORY       The directory where the Cyber Hygiene
                                    PDF reports are located.  If not
                                    specified then no Cyber Hygiene reports
                                    will be sent.
  --tmail-report-dir=DIRECTORY      The directory where the trustymail PDF
                                    reports are located.  If not specified then
                                    no trustymail reports will be sent.
  --https-report-dir=DIRECTORY      The directory where the https-scan PDF
                                    reports are located.  If not specified then
                                    no https-scan reports will be sent.
  --cybex-scorecard-dir=DIRECTORY   The directory where the Cybex PDF
                                    scorecard is located.  If not specified
                                    then no Cybex scorecard will be sent.
  --cyhy-notification-dir=DIRECTORY The directory where the Cyber Hygiene
                                    Notification PDF reports are located.  If
                                    not specified then no Cyber Hygiene
                                    notifications will be sent.
  -c --db-creds-file=FILENAME       A YAML file containing the Cyber
                                    Hygiene database credentials.
                                    [default: /run/secrets/database_creds.yml]
  --batch-size=SIZE                 The batch size to use when retrieving
                                    results from the Mongo database.  If not
                                    present then the default Mongo batch size
                                    will be used.
  --summary-to=EMAILS               A comma-separated list of email addresses
                                    to which the summary statistics should be
                                    sent at the end of the run.  If not
                                    specified then no summary will be sent.
  -d --debug                        Include debugging messages in the output.
  --dry-run                         Do everything except actually send out
                                    emails.

"""

# Standard Python Libraries
import datetime
import glob
import logging
import re

# Third-Party Libraries
import boto3
from botocore.exceptions import ClientError
import docopt
import pymongo.errors
import yaml

# cisagov Libraries
from cyhy.mailer import __version__
from cyhy.mailer.CybexMessage import CybexMessage
from cyhy.mailer.CyhyMessage import CyhyMessage
from cyhy.mailer.CyhyNotificationMessage import CyhyNotificationMessage
from cyhy.mailer.HttpsMessage import HttpsMessage
from cyhy.mailer.ReportMessage import ReportMessage
from cyhy.mailer.StatsMessage import StatsMessage
from cyhy.mailer.TmailMessage import TmailMessage
from mongo_db_from_config import db_from_config


class Error(Exception):
    """A base class for exceptions used in this module."""

    pass


def get_emails_from_request(request):
    """Return the agency's correspondence email address(es).

    Given the request document, return the proper email address or
    addresses to use for corresponding with the agency.

    Parameters
    ----------
    request : dict
        The request documents for which the corresponding email
        address is desired.

    Returns
    -------
    list of str: A list containing the proper email addresses to use
    for corresponding with the agency

    """
    id = request["_id"]
    # Drop any contacts that do not have both a type and a non-empty email
    # attribute...
    contacts = [
        c
        for c in request["agency"]["contacts"]
        if "type" in c and "email" in c and c["email"].split()
    ]
    # ...but let's log a warning about them.
    for c in request["agency"]["contacts"]:
        if "type" not in c or "email" not in c or not c["email"].split():
            logging.warn(
                f"Agency with ID {id} has a contact that is missing an email and/or type attribute!"
            )

    distro_emails = [c["email"] for c in contacts if c["type"] == "DISTRO"]
    technical_emails = [c["email"] for c in contacts if c["type"] == "TECHNICAL"]

    # There should be zero or one distro email, so log a warning if
    # there are multiple.
    if len(distro_emails) > 1:
        logging.warn(f"More than one DISTRO email address for agency with ID {id}")

    # Send to the distro email, if it exists.  Otherwise, send to the
    # technical emails.
    to_emails = distro_emails
    if not to_emails:
        to_emails = technical_emails

    # At this point to_emails should contain at least one email
    if not to_emails:
        logging.error(f"No emails found for ID {id}")

    return to_emails


def get_all_descendants(db, parent):
    """Return all (non-retired) descendants of the parent.

    Parameters
    ----------
    db : MongoDatabase
        The Mongo database from which request document data can be
        retrieved.

    parent : str
        The parent for which all descendants are desired.

    Returns
    -------
    list(str): The descendants of the parent.

    Throws
    ------
    ValueError: If there is no request document corresponding to the
    specified parent.

    """
    current_request = db.requests.find_one({"_id": parent})
    if not current_request:
        raise ValueError(parent + " has no request document")

    descendants = []
    if current_request.get("children"):
        for child in current_request["children"]:
            if not db.requests.find_one({"_id": child}).get("retired"):
                descendants.append(child)
                descendants += get_all_descendants(db, child)

    # Remove duplicates
    return list(set(descendants))


def get_requests_raw(db, query, batch_size=None):
    """Return a cursor for iterating over agencies' request documents.

    Parameters
    ----------
    db : MongoDatabase
        The Mongo database from which agency data can be retrieved.

    query : dict
        The query to perform.

    batch_size : int
        The batch size to use when retrieving results from the Mongo
        database.  If None then the default will be used.

    Returns
    -------
    pymongo.cursor.Cursor: A cursor that can be used to iterate over
    the request documents.

    Throws
    ------
    pymongo.errors.TypeError: If unable to connect to the requested
    server, or if batch_size is not an int or None.

    pymongo.errors.InvalidOperation: If the cursor has already been
    used.  The batch size cannot be set on a cursor that has already
    been used.

    """
    projection = {
        "_id": True,
        "agency.acronym": True,
        "agency.contacts.name": True,
        "agency.contacts.email": True,
        "agency.contacts.type": True,
    }

    try:
        requests = db.requests.find(query, projection)
        if batch_size is not None:
            requests.batch_size(batch_size)
    except TypeError:
        logging.critical(
            "There was an error with the MongoDB query that retrieves the request documents",
            exc_info=True,
        )
        raise

    return requests


def get_requests(db, report_types=None, federal_only=False, batch_size=None):
    """Return a cursor for iterating over agencies' request documents.

    Parameters
    ----------
    db : MongoDatabase
        The Mongo database from which agency data can be retrieved.

    report_types : list(str)
        A list of report types (e.g. CYHY, CYBEX, BOD).  Only agencies
        whose request documents specify these report types will be
        returned.  If None then no such restriction is placed on the
        query.

    federal_only : bool
        If True then only federal agencies' request documents will be
        returned.  If unspecified or False then no such restriction is
        placed on the query.

    batch_size : int
        The batch size to use when retrieving results from the Mongo
        database.  If None then the default will be used.

    Returns
    -------
    pymongo.cursor.Cursor: A cursor that can be used to iterate over
    the request documents.

    Throws
    ------
    pymongo.errors.TypeError: If unable to connect to the requested
    server, or if batch_size is not an int or None.

    ValueError: If batch_size is negative, or if there is no FEDERAL
    category in the database but federal_only is True.

    pymongo.errors.InvalidOperation: If the cursor has already been
    used.  The batch size cannot be set on a cursor that has already
    been used.

    """
    query = {"retired": {"$ne": True}}
    if federal_only:
        fed_orgs = get_all_descendants(db, "FEDERAL")
        query["_id"] = {"$in": fed_orgs}

    if report_types is not None:
        query["report_types"] = {"$in": report_types}

    return get_requests_raw(db, query, batch_size)


class UnableToSendError(Exception):
    """Raise when an error is encountered when sending an email.

    Attributes
    ----------
    response : dict
        The response returned by boto3.

    """

    def __init__(self, response):
        """Initialize."""
        self.response = response


def send_message(ses_client, message, counter=None, dry_run=False):
    """Send a message.

    Parameters
    ----------
    ses_client : boto3.client
        The boto3 SES client via which the message is to be sent.

    message : email.message.Message
        The email message that is to be sent.

    counter : int
        A counter.

    dry_run : bool
        If True then do not actually send email.

    Returns
    -------
    int: If counter was not None, then counter + 1 is returned if the
    message was sent sent successfully and counter is returned if not.
    If counter was None then None is returned.

    Throws
    ------
    ClientError: If an error is encountered when attempting to send
    the message.

    UnableToSendError: If the response from sending the message is
    anything other than 200.

    """
    if not dry_run:
        # "Are you silly?  I'm still gonna send it!"
        #   -- Larry Enticer
        response = ses_client.send_raw_email(RawMessage={"Data": message.as_string()})

        # Check for errors
        status_code = response["ResponseMetadata"]["HTTPStatusCode"]
        if status_code != 200:
            logging.error(
                f"Unable to send message.  Response from boto3 is: {response}"
            )
            raise UnableToSendError(response)
    else:
        logging.debug("NOT sending message (dry run)")

    if counter is not None:
        counter += 1

    return counter


def send_bod_reports(
    db, batch_size, ses_client, tmail_report_dir, https_report_dir, dry_run=False
):
    """Send out Trustworthy Email and HTTPS reports.

    Parameters
    ----------
    db : MongoDatabase
        The Mongo database from which Cyber Hygiene agency data can
        be retrieved.

    batch_size : int
        The batch size to use when retrieving results from the Mongo
        database.  If None then the default will be used.

    ses_client : boto3.client
        The boto3 SES client via which the message is to be sent.

    tmail_report_dir : str
        The directory where the Trustworthy Email reports can be
        found.  If None then no Trustworthy Email reports will be
        sent.

    https_report_dir : str
        The directory where the HTTPS reports can be found.  If None
        then no HTTPS reports will be sent.

    dry_run : bool
        If True then do not actually send email.

    Returns
    -------
    tuple(str): A tuple of strings that summarizes what was sent.

    """
    try:
        fed_orgs = get_all_descendants(db, "FEDERAL")
        # We want all non-retired request docs with either (1) a
        # report type of BOD or (2) a report type of CYHY and
        # corresponding to a federal stakeholder.  This is a
        # complicated query, so we construct it manually.
        query = {
            "$and": [
                {"retired": {"$ne": True}},
                {
                    "$or": [
                        {"report_types": {"$in": ["BOD"]}},
                        {
                            "$and": [
                                {"_id": {"$in": fed_orgs}},
                                {"report_types": {"$in": ["CYHY"]}},
                            ]
                        },
                    ]
                },
            ]
        }
        bod_requests = get_requests_raw(db, query, batch_size)

    except TypeError:
        return 4

    try:
        bod_agencies = bod_requests.count()
        logging.debug(f"BOD 18-01 agencies = {bod_agencies}")
    except pymongo.errors.OperationFailure:
        logging.critical(
            "Mongo database error while counting the number of request documents returned",
            exc_info=True,
        )
    agencies_emailed_tmail_reports = 0
    agencies_emailed_https_reports = 0

    ###
    # Iterate over bod_requests
    ###
    for request in bod_requests:
        id = request["_id"]
        acronym = request["agency"]["acronym"]

        to_emails = get_emails_from_request(request)
        # to_emails should contain at least one email
        if not to_emails:
            continue

        ###
        # Find and mail the trustymail report, if necessary
        #
        # This is very similar to the CyHy block but slightly
        # different.  I need to figure out how to isolate the common
        # functionality into a class or functions.
        ###
        if tmail_report_dir:
            # The '2' is necessary because in some cases we have both XYZ and
            # XYZ-AB as stakeholders.  Without the '2' the glob would include
            # both for the ID XYZ.
            tmail_report_glob = f"{tmail_report_dir}/cyhy-{id}-2*.pdf"
            tmail_report_filenames = sorted(glob.glob(tmail_report_glob))

            # At most one Tmail report should match
            if len(tmail_report_filenames) > 1:
                logging.warn(
                    f"More than one Trustworthy Email report found for agency with ID {id}"
                )
            elif not tmail_report_filenames:
                # This is only at info since we are starting from the
                # list of CyHy agencys.  Many of them will not have
                # Tmail reports.
                logging.info(
                    f"No Trustworthy Email report found for agency with ID {id}"
                )

            if tmail_report_filenames:
                # We take the last filename since, if there happens to be more
                # than one, it should the latest.  (This is because we sorted
                # the glob results.)
                tmail_attachment_filename = tmail_report_filenames[-1]

                # Extract the report date from the report filename
                match = re.search(
                    r"-(?P<date>\d{4}-[01]\d-[0-3]\d)-tmail-report",
                    tmail_attachment_filename,
                )
                report_date = datetime.datetime.strptime(
                    match.group("date"), "%Y-%m-%d"
                ).strftime("%B %d, %Y")

                # Construct the Tmail message to send
                message = TmailMessage(
                    to_emails, tmail_attachment_filename, acronym, report_date
                )

                try:
                    agencies_emailed_tmail_reports = send_message(
                        ses_client, message, agencies_emailed_tmail_reports, dry_run
                    )
                except (UnableToSendError, ClientError):
                    logging.error(
                        f"Unable to send Trustworthy Email report for agency with ID {id}",
                        exc_info=True,
                        stack_info=True,
                    )

        ###
        # Find and mail the https report, if necessary
        #
        # This is very similar to the CyHy block but slightly
        # different.  I need to figure out how to isolate the common
        # functionality into a class or functions.
        ###
        if https_report_dir:
            # The '2' is necessary because in some cases we have both XYZ and
            # XYZ-AB as stakeholders.  Without the '2' the glob would include
            # both for the ID XYZ.
            https_report_glob = f"{https_report_dir}/cyhy-{id}-2*.pdf"
            https_report_filenames = sorted(glob.glob(https_report_glob))

            # At most one HTTPS report should match
            if len(https_report_filenames) > 1:
                logging.warn(
                    f"More than one HTTPS report found for agency with ID {id}"
                )
            elif not https_report_filenames:
                # This is only at info since we are starting from the
                # list of CyHy agencys.  Many of them will not have
                # HTTPS reports.
                logging.info(f"No HTTPS report found for agency with ID {id}")

            if https_report_filenames:
                # We take the last filename since, if there happens to be more
                # than one, it should the latest.  (This is because we sorted
                # the glob results.)
                https_attachment_filename = https_report_filenames[-1]

                # Extract the report date from the report filename
                match = re.search(
                    r"-(?P<date>\d{4}-[01]\d-[0-3]\d)-https-report",
                    https_attachment_filename,
                )
                report_date = datetime.datetime.strptime(
                    match.group("date"), "%Y-%m-%d"
                ).strftime("%B %d, %Y")

                # Construct the HTTPS message to send
                message = HttpsMessage(
                    to_emails, https_attachment_filename, acronym, report_date
                )

                try:
                    agencies_emailed_https_reports = send_message(
                        ses_client, message, agencies_emailed_https_reports, dry_run
                    )
                except (UnableToSendError, ClientError):
                    logging.error(
                        f"Unable to send HTTPS report for agency with ID {id}",
                        exc_info=True,
                        stack_info=True,
                    )

    # Print out and log some statistics
    tmail_stats_string = f"Out of {bod_agencies} Federal BOD 18-01 agencies, {agencies_emailed_tmail_reports} ({100.0 * agencies_emailed_tmail_reports / bod_agencies:.2f}%) were emailed Trustworthy Email reports."
    https_stats_string = f"Out of {bod_agencies} Federal BOD 18-01 agencies, {agencies_emailed_https_reports} ({100.0 * agencies_emailed_https_reports / bod_agencies:.2f}%) were emailed HTTPS reports."
    logging.info(tmail_stats_string)
    logging.info(https_stats_string)
    print(tmail_stats_string)
    print(https_stats_string)

    return (tmail_stats_string, https_stats_string)


def send_cybex_scorecard(
    db, batch_size, ses_client, cybex_scorecard_dir, dry_run=False
):
    """Send out Cyber Exposure scorecard.

    Parameters
    ----------
    db : MongoDatabase
        The Mongo database from which Cyber Hygiene agency data can
        be retrieved.

    batch_size : int
        The batch size to use when retrieving results from the Mongo
        database.  If None then the default will be used.

    ses_client : boto3.client
        The boto3 SES client via which the message is to be sent.

    cybex_scorecard_dir : str
        The directory where the Cybex scorecard can be found.  If None
        then no Cybex scorecard will be sent.

    dry_run : bool
        If True then do not actually send email.

    Returns
    -------
    tuple(str): A tuple of strings that summarizes what was sent.

    """
    cybex_report_emailed = False

    ###
    # Find and mail the Cybex report, if necessary
    #
    # This is very similar to the CyHy block but slightly different.
    # I need to figure out how to isolate the common functionality
    # into a class or functions.
    ###
    if cybex_scorecard_dir:
        cybex_report_glob = (
            f"{cybex_scorecard_dir}/Federal_Cyber_Exposure_Scorecard-*.pdf"
        )
        cybex_report_filenames = sorted(glob.glob(cybex_report_glob))
        cybex_risky_services_open_csv_glob = (
            f"{cybex_scorecard_dir}/cybex_open_tickets_potentially_risky_services_*.csv"
        )
        cybex_risky_services_open_csv_filenames = sorted(
            glob.glob(cybex_risky_services_open_csv_glob)
        )
        cybex_risky_services_closed_csv_glob = f"{cybex_scorecard_dir}/cybex_closed_tickets_potentially_risky_services_*.csv"
        cybex_risky_services_closed_csv_filenames = sorted(
            glob.glob(cybex_risky_services_closed_csv_glob)
        )
        cybex_urgent_open_csv_glob = (
            f"{cybex_scorecard_dir}/cybex_open_tickets_urgent_*.csv"
        )
        cybex_urgent_open_csv_filenames = sorted(glob.glob(cybex_urgent_open_csv_glob))
        cybex_urgent_closed_csv_glob = (
            f"{cybex_scorecard_dir}/cybex_closed_tickets_urgent_*.csv"
        )
        cybex_urgent_closed_csv_filenames = sorted(
            glob.glob(cybex_urgent_closed_csv_glob)
        )

        # At most one Cybex report and CSV should match
        if len(cybex_report_filenames) > 1:
            logging.warn("More than one CybEx scorecard found")
        elif not cybex_report_filenames:
            logging.error("No CybEx scorecard found")
        if len(cybex_risky_services_open_csv_filenames) > 1:
            logging.warn("More than one CybEx risky services open CSV found")
        elif not cybex_risky_services_open_csv_filenames:
            logging.error("No CybEx risky services open CSV found")
        if len(cybex_risky_services_closed_csv_filenames) > 1:
            logging.warn("More than one CybEx risky services closed CSV found")
        elif not cybex_risky_services_closed_csv_filenames:
            logging.error("No CybEx risky services closed CSV found")
        if len(cybex_urgent_open_csv_filenames) > 1:
            logging.warn("More than one CybEx urgent open CSV found")
        elif not cybex_urgent_open_csv_filenames:
            logging.error("No CybEx urgent open CSV found")
        if len(cybex_urgent_closed_csv_filenames) > 1:
            logging.warn("More than one CybEx urgent closed CSV found")
        elif not cybex_urgent_closed_csv_filenames:
            logging.error("No CybEx urgent closed CSV found")

        if (
            cybex_report_filenames
            and cybex_risky_services_open_csv_filenames
            and cybex_risky_services_closed_csv_filenames
            and cybex_urgent_open_csv_filenames
            and cybex_urgent_closed_csv_filenames
        ):
            # We take the last filename since, if there happens to be more than
            # one, it should be the latest.  (This is because we sorted the glob
            # results.)
            cybex_report_filename = cybex_report_filenames[-1]
            cybex_risky_services_open_csv_filename = (
                cybex_risky_services_open_csv_filenames[-1]
            )
            cybex_risky_services_closed_csv_filename = (
                cybex_risky_services_closed_csv_filenames[-1]
            )
            cybex_urgent_open_csv_filename = cybex_urgent_open_csv_filenames[-1]
            cybex_urgent_closed_csv_filename = cybex_urgent_closed_csv_filenames[-1]

            # Extract the report date from the report filename
            match = re.search(
                r"Federal_Cyber_Exposure_Scorecard-(?P<date>\d{4}-[01]\d-[0-3]\d)",
                cybex_report_filename,
            )
            report_date = datetime.datetime.strptime(
                match.group("date"), "%Y-%m-%d"
            ).strftime("%B %d, %Y")

            # Construct the Cybex message to send
            message = CybexMessage(
                cybex_report_filename,
                cybex_risky_services_open_csv_filename,
                cybex_risky_services_closed_csv_filename,
                cybex_urgent_open_csv_filename,
                cybex_urgent_closed_csv_filename,
                report_date,
            )

            try:
                cybex_report_emailed = bool(
                    send_message(ses_client, message, 0, dry_run)
                )
            except (UnableToSendError, ClientError):
                logging.error(
                    "Unable to send Cyber Exposure Scorecard",
                    exc_info=True,
                    stack_info=True,
                )

    # Print out and log some statistics
    if cybex_report_emailed:
        cybex_stats_string = "Cyber Exposure scorecard was emailed."
    else:
        cybex_stats_string = "Cyber Exposure scorecard was not emailed."
    logging.info(cybex_stats_string)
    print(cybex_stats_string)

    return (cybex_stats_string,)


def send_cyhy_reports(db, batch_size, ses_client, cyhy_report_dir, dry_run=False):
    """Send out Cyber Hygiene reports.

    Parameters
    ----------
    db : MongoDatabase
        The Mongo database from which Cyber Hygiene agency data can
        be retrieved.

    batch_size : int
        The batch size to use when retrieving results from the Mongo
        database.  If None then the default will be used.

    ses_client : boto3.client
        The boto3 SES client via which the message is to be sent.

    cyhy_report_dir : str
        The directory where the Cyber Hygiene reports can be found.
        If None then no Cyber Hygiene reports will be sent.

    dry_run : bool
        If True then do not actually send email.

    Returns
    -------
    tuple(str): A tuple of strings that summarizes what was sent.

    """
    try:
        cyhy_requests = get_requests(
            db, report_types=["CYHY", "CYHY_THIRD_PARTY"], batch_size=batch_size
        )
    except TypeError:
        return 4

    try:
        cyhy_agencies = cyhy_requests.count()
        logging.debug(f"Cyber Hygiene agencies = {cyhy_agencies}")
    except pymongo.errors.OperationFailure:
        logging.critical(
            "Mongo database error while counting the number of request documents returned",
            exc_info=True,
        )
    agencies_emailed_cyhy_reports = 0
    sample_cyhy_report_emailed = False

    ###
    # Iterate over cyhy_requests, if necessary
    ###
    if cyhy_report_dir:
        for request in cyhy_requests:
            id = request["_id"]
            acronym = request["agency"]["acronym"]
            technical_pocs = [
                contact
                for contact in request["agency"]["contacts"]
                if contact["type"] == "TECHNICAL"
            ]

            to_emails = get_emails_from_request(request)
            # to_emails should contain at least one email
            if not to_emails:
                continue

            ###
            # Find and mail the CyHy report, if necessary
            ###

            # The '2' is necessary because in some cases we have both XYZ and
            # XYZ-AB as stakeholders.  Without the '2' the glob would include
            # both for the ID XYZ.
            cyhy_report_glob = f"{cyhy_report_dir}/cyhy-{id}-2*.pdf"
            cyhy_report_filenames = sorted(glob.glob(cyhy_report_glob))

            # Exactly one CyHy report should match
            if len(cyhy_report_filenames) > 1:
                logging.warn(
                    f"More than one Cyber Hygiene report found for agency with ID {id}"
                )
            elif not cyhy_report_filenames:
                # This is an error since we are starting from the list
                # of CyHy agencies and they should all have reports.
                #
                # It is possible to get this error if a CyHy request
                # doc has "CYHY_THIRD_PARTY" in its report_types, but
                # it does not have any children (the reporting code
                # skips these request docs).
                logging.error(f"No Cyber Hygiene report found for agency with ID {id}")

            if cyhy_report_filenames:
                # We take the last filename since, if there happens to be more
                # than one, it should the latest.  (This is because we sorted
                # the glob results.)
                cyhy_attachment_filename = cyhy_report_filenames[-1]

                # Extract the report date from the report filename
                match = re.search(
                    r"-(?P<date>\d{4}-[01]\d-[0-3]\d)T", cyhy_attachment_filename
                )
                report_date = datetime.datetime.strptime(
                    match.group("date"), "%Y-%m-%d"
                ).strftime("%B %d, %Y")

                # Construct the CyHy message to send
                message = CyhyMessage(
                    to_emails,
                    cyhy_attachment_filename,
                    acronym,
                    report_date,
                    technical_pocs,
                )

                try:
                    agencies_emailed_cyhy_reports = send_message(
                        ses_client, message, agencies_emailed_cyhy_reports, dry_run
                    )
                except (UnableToSendError, ClientError):
                    logging.error(
                        f"Unable to send Cyber Hygiene report for agency with ID {id}",
                        exc_info=True,
                        stack_info=True,
                    )

        ###
        # Find and mail the CyHy sample report, if it is present
        ###

        # The '2' is necessary because in some cases we have both XYZ and
        # XYZ-AB as stakeholders.  Without the '2' the glob would include both
        # for the ID XYZ.
        cyhy_sample_report_glob = f"{cyhy_report_dir}/cyhy-SAMPLE-2*.pdf"
        cyhy_sample_report_filenames = sorted(glob.glob(cyhy_sample_report_glob))

        # Exactly one CyHy sample report should match
        if len(cyhy_sample_report_filenames) > 1:
            logging.warn("More than one Cyber Hygiene sample report found")
        elif not cyhy_sample_report_filenames:
            logging.warn("No Cyber Hygiene sample report found")

        if cyhy_sample_report_filenames:
            # We take the last filename since, if there happens to be more than
            # one, it should the latest.  (This is because we sorted the glob
            # results.)
            cyhy_attachment_filename = cyhy_sample_report_filenames[-1]

            # Extract the report date from the report filename
            match = re.search(
                r"-(?P<date>\d{4}-[01]\d-[0-3]\d)T", cyhy_attachment_filename
            )
            report_date = datetime.datetime.strptime(
                match.group("date"), "%Y-%m-%d"
            ).strftime("%B %d, %Y")

            # Construct the report message to send
            subject = f"Sample Cyber Hygiene Report - {report_date}"
            message = ReportMessage(
                ["vulnerability@cisa.dhs.gov"],
                subject,
                None,
                None,
                cyhy_attachment_filename,
                cc_addrs=None,
            )

            try:
                sample_cyhy_report_emailed = bool(
                    send_message(ses_client, message, 0, dry_run)
                )
            except (UnableToSendError, ClientError):
                logging.error(
                    "Unable to send sample Cyber Hygiene report",
                    exc_info=True,
                    stack_info=True,
                )

    # Print out and log some statistics
    cyhy_stats_string = f"Out of {cyhy_agencies} Cyber Hygiene agencies, {agencies_emailed_cyhy_reports} ({100.0 * agencies_emailed_cyhy_reports / cyhy_agencies:.2f}%) were emailed Cyber Hygiene reports."
    if sample_cyhy_report_emailed:
        sample_cyhy_stats_string = "Sample Cyber Hygiene report was emailed."
    else:
        sample_cyhy_stats_string = "Sample Cyber Hygiene report was not emailed."
    logging.info(cyhy_stats_string)
    logging.info(sample_cyhy_stats_string)
    print(cyhy_stats_string)
    print(sample_cyhy_stats_string)

    return (cyhy_stats_string, sample_cyhy_stats_string)


def send_cyhy_notifications(
    db, batch_size, ses_client, cyhy_notification_dir, dry_run=False
):
    """Send out Cyber Hygiene reports notifications.

    Parameters
    ----------
    db : MongoDatabase
        The Mongo database from which Cyber Hygiene agency data can
        be retrieved.

    batch_size : int
        The batch size to use when retrieving results from the Mongo
        database.  If None then the default will be used.

    ses_client : boto3.client
        The boto3 SES client via which the message is to be sent.

    cyhy_notification_dir : str
        The directory where the Cyber Hygiene notifications can be found.
        If None then no Cyber Hygiene notifications will be sent.

    dry_run : bool
        If True then do not actually send email.

    Returns
    -------
    tuple(str): A tuple of strings that summarizes what was sent.

    """
    try:
        # Get request docs for all orgs that receive CyHy reports
        cyhy_requests = get_requests(
            db, report_types=["CYHY"], federal_only=False, batch_size=batch_size
        )
    except TypeError:
        return 4

    try:
        cyhy_agencies = cyhy_requests.count()
        logging.debug(f"Cyber Hygiene notification agencies = {cyhy_agencies}")
    except pymongo.errors.OperationFailure:
        logging.critical(
            "Mongo database error while counting the number of request documents returned",
            exc_info=True,
        )
    agencies_emailed_cyhy_notifications = 0

    fed_orgs = get_all_descendants(db, "FEDERAL")

    ###
    # Iterate over cyhy_notification_requests
    ###
    for request in cyhy_requests:
        id = request["_id"]
        acronym = request["agency"]["acronym"]
        is_federal = id in fed_orgs

        to_emails = get_emails_from_request(request)
        # to_emails should contain at least one email
        if not to_emails:
            continue

        ###
        # Find and mail the CyHy notifications, if necessary
        ###
        if cyhy_notification_dir:
            # The '2' is necessary because in some cases we have both XYZ and
            # XYZ-AB as stakeholders.  Without the '2' the glob would include
            # both for the ID XYZ.
            cyhy_notification_glob = (
                f"{cyhy_notification_dir}/" f"cyhy-notification-{id}-2*.pdf"
            )
            cyhy_notification_filenames = sorted(glob.glob(cyhy_notification_glob))

            # No more than one CyHy notification should match
            # It is fine if there are zero matches; that means there are no
            # notifications to be sent out for this stakeholder
            if len(cyhy_notification_filenames) > 1:
                logging.warn(
                    f"More than one Cyber Hygiene notification found for agency with ID {id}"
                )

            if cyhy_notification_filenames:
                # We take the last filename since, if there happens to be more
                # than one, it should send the latest one.
                # (This is because we sorted the glob results.)
                cyhy_notification_attachment_filename = cyhy_notification_filenames[-1]

                # Extract the date from the notification filename
                match = re.search(
                    r"-(?P<date>\d{4}-[01]\d-[0-3]\d)T",
                    cyhy_notification_attachment_filename,
                )
                notification_date = datetime.datetime.strptime(
                    match.group("date"), "%Y-%m-%d"
                ).strftime("%B %d, %Y")

                # Construct the CyHy notification message to send
                message = CyhyNotificationMessage(
                    to_emails,
                    cyhy_notification_attachment_filename,
                    acronym,
                    is_federal,
                    notification_date,
                )

                try:
                    agencies_emailed_cyhy_notifications = send_message(
                        ses_client,
                        message,
                        agencies_emailed_cyhy_notifications,
                        dry_run,
                    )
                except (UnableToSendError, ClientError):
                    logging.error(
                        f"Unable to send Cyber Hygiene notification for agency with ID {id}",
                        exc_info=True,
                        stack_info=True,
                    )

    # Print out and log some statistics
    cyhy_notification_stats_string = f"Out of {cyhy_agencies} Cyber Hygiene agencies, {agencies_emailed_cyhy_notifications} ({100.0 * agencies_emailed_cyhy_notifications / cyhy_agencies:.2f}%) were emailed Cyber Hygiene notifications."
    logging.info(cyhy_notification_stats_string)
    print(cyhy_notification_stats_string)

    return (cyhy_notification_stats_string,)


def main():
    """Send emails."""
    # Parse command line arguments
    args = docopt.docopt(__doc__, version=__version__)

    # Set up logging
    log_level = logging.WARNING
    if args["--debug"]:
        log_level = logging.DEBUG
    logging.basicConfig(
        format="%(asctime)-15s %(levelname)s %(message)s", level=log_level
    )

    db_creds_file = args["--db-creds-file"]
    try:
        db = db_from_config(db_creds_file)
    except OSError:
        logging.critical(
            f"Database configuration file {db_creds_file} does not exist", exc_info=True
        )
        return 1
    except yaml.YAMLError:
        logging.critical(
            f"Database configuration file {db_creds_file} does not contain valid YAML",
            exc_info=True,
        )
        return 1
    except KeyError:
        logging.critical(
            f"Database configuration file {db_creds_file} does not contain the expected keys",
            exc_info=True,
        )
        return 1
    except pymongo.errors.ConnectionError:
        logging.critical(
            f"Unable to connect to the database server in {db_creds_file}",
            exc_info=True,
        )
        return 1
    except pymongo.errors.InvalidName:
        logging.critical(
            f"The database in {db_creds_file} does not exist", exc_info=True
        )
        return 1

    ses_client = boto3.client("ses")

    batch_size = args["--batch-size"]
    if batch_size is not None:
        try:
            batch_size = int(batch_size)
        except ValueError:
            logging.critical(
                f'The value {args["--batch-size"]} cannot be interpreted as an integer',
                exc_info=True,
            )
            return 4

    ###
    # Send reports and gather summary statistics
    ###
    all_stats_strings = []

    if args["bod1801"]:
        stats = send_bod_reports(
            db,
            batch_size,
            ses_client,
            args["--tmail-report-dir"],
            args["--https-report-dir"],
            args["--dry-run"],
        )
        all_stats_strings.extend(stats)

    if args["cybex"]:
        stats = send_cybex_scorecard(
            db, batch_size, ses_client, args["--cybex-scorecard-dir"], args["--dry-run"]
        )
        all_stats_strings.extend(stats)

    if args["cyhy"]:
        stats = send_cyhy_reports(
            db, batch_size, ses_client, args["--cyhy-report-dir"], args["--dry-run"]
        )
        all_stats_strings.extend(stats)

    if args["notification"]:
        stats = send_cyhy_notifications(
            db,
            batch_size,
            ses_client,
            args["--cyhy-notification-dir"],
            args["--dry-run"],
        )
        all_stats_strings.extend(stats)

    ###
    # Email the summary statistics, if necessary
    ###
    summary_to = args["--summary-to"]
    if summary_to and all_stats_strings:
        message = StatsMessage(summary_to.split(","), all_stats_strings)
        try:
            send_message(ses_client, message, dry_run=args["--dry-run"])
        except (UnableToSendError, ClientError):
            logging.error(
                "Unable to send cyhy-mailer report summary",
                exc_info=True,
                stack_info=True,
            )
    else:
        logging.warn("Nothing was emailed.")
        print("Nothing was emailed.")

    # Stop logging and clean up
    logging.shutdown()


if __name__ == "__main__":
    main()
