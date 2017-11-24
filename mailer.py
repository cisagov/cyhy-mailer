#!/usr/bin/env python

import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
 
msg = MIMEMultipart()
 
msg['From'] = 'ncats@hq.dhs.gov'
msg['To'] = 'jeremy.frasier@beta.dhs.gov'
msg['CC'] = 'ncats@hq.dhs.gov'
msg['Subject'] = 'AGENCY_ACRONYM - CyHy - FY# Q# Results'
 
body = """Greetings AGENCY_ACRONYM,
The Cyber Hygiene scan results are attached for your review. Same password as before. (If this is your first report and you have yet to receive a password, please let us know!)
If you have any questions, please contact our office.

Cheers, 
The NCATS team

National Cybersecurity Assessments and Technical Services (NCATS)
National Cybersecurity and Communications Integration Center
U.S. Department of Homeland Security
ncats@hq.dhs.gov

WARNING: This document is FOR OFFICIAL USE ONLY (FOUO). It contains information that may be exempt from public release under the Freedom of Information Act (5 U.S.G. 552). It is to be controlled, stored, handled, transmitted, distributed, and disposed of in accordance with DHS policy relating to FOUO information and is not to be released to the public or other personnel who do not have a valid 'need-to-know' without prior approval of an authorized DHS official.
"""
 
msg.attach(MIMEText(body, 'plain'))
 
filename = 'cyhy-DHS-2017-11-24-tmail-report.pdf'
attachment = open('/home/jeremy_frasier/trustymail_reports_2017-11-24/artifacts_2017-11-24/reporting/reports/cyhy-DHS-2017-11-24-tmail-report.pdf', 'rb')
 
part = MIMEBase('application', 'octet-stream')
part.set_payload(attachment.read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
 
msg.attach(part)
 
server = smtplib.SMTP('smtp01.ncats.dhs.gov', 25)
#server.starttls()
#server.login('')
text = msg.as_string()
server.sendmail(msg['From'], msg['To'], text)
server.quit()

#TO: Pull DISTRO email from cyhy database; if no DISTRO exists, send to every TECHNICAL POC
#CC: NCATS@hq.dhs.gov
#Subject: AGENCY_ACRONYM - CyHy - FY# Q# Results
#Attachment: Cyber Hygiene Report
