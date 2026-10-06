"""Binary report parts have exactly one transfer-encoding header."""

# Standard Python Libraries
from email import policy
from email.parser import BytesParser, Parser
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

# cisagov Libraries
from cyhy.mailer.Message import Message
from cyhy.mailer.ReportMessage import ReportMessage
from cyhy.mailer.cli import send_message


class AttachmentTransferEncodingTest(unittest.TestCase):
    """Check MIME construction and serialized messages without sending mail."""

    def setUp(self):
        """Write opaque attachment bytes into an isolated temporary directory."""
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "report.pdf"
        self.data = bytes(range(256)) + b"\r\nreport attachment\x00"
        self.path.write_bytes(self.data)

    def assert_attachment(self, message, expected_name="report.pdf"):
        """Check bytes, filename and a single explicit base64 header."""
        parts = [
            part
            for part in message.walk()
            if part.get_content_type() == "application/pdf"
        ]
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0].get_all("Content-Transfer-Encoding"), ["base64"])
        self.assertEqual(parts[0].get_payload(decode=True), self.data)
        self.assertEqual(parts[0].get_filename(), expected_name)

    def test_direct_attachment_uses_the_default_mime_encoder_once(self):
        """Do not add a second header to an already encoded application part."""
        message = Message(["recipient@example.test"])
        message.attach_pdf(str(self.path))
        self.assert_attachment(message)

    def test_report_message_survives_smtp_serialization(self):
        """The public report constructor produces a single encoded MIME part."""
        message = ReportMessage(
            ["recipient@example.test"],
            "Report",
            "Plain text",
            "<p>Report</p>",
            str(self.path),
        )
        parsed = BytesParser(policy=policy.default).parsebytes(
            message.as_bytes(policy=policy.SMTP)
        )
        self.assert_attachment(parsed)
        self.assertEqual(
            parsed.get_body(preferencelist=("plain",)).get_content().strip(),
            "Plain text",
        )

    def test_multiple_attachments_are_each_encoded_once(self):
        """Each attachment has independent headers and unchanged binary data."""
        message = Message(["recipient@example.test"])
        for name, content in [
            ("first.pdf", self.data),
            ("second.pdf", b""),
            ("third-report.pdf", b"other\x00\xff"),
        ]:
            path = Path(self.directory.name) / name
            path.write_bytes(content)
            message.attach_pdf(str(path))
        parsed = BytesParser(policy=policy.default).parsebytes(
            message.as_bytes(policy=policy.SMTP)
        )
        parts = list(parsed.iter_attachments())
        self.assertEqual(len(parts), 3)
        for part, content in zip(parts, [self.data, b"", b"other\x00\xff"]):
            self.assertEqual(part.get_all("Content-Transfer-Encoding"), ["base64"])
            self.assertEqual(part.get_payload(decode=True), content)
        self.assertEqual(parts[-1].get_filename(), "third-report.pdf")

    def test_ses_submission_receives_a_single_encoding_header(self):
        """Intercept the actual send helper before any external API call."""
        message = Message(
            ["recipient@example.test"], subject="Report", text_body="Body"
        )
        message.attach_pdf(str(self.path))
        client = Mock()
        client.send_email.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
        self.assertEqual(send_message(client, message, counter=0), 1)
        client.send_email.assert_called_once()
        raw = client.send_email.call_args.kwargs["Content"]["Raw"]["Data"]
        self.assert_attachment(Parser(policy=policy.default).parsestr(raw))

    def test_dry_run_does_not_call_ses(self):
        """The transport control remains unchanged."""
        message = Message(["recipient@example.test"])
        message.attach_pdf(str(self.path))
        client = Mock()
        self.assertEqual(send_message(client, message, counter=0, dry_run=True), 1)
        client.send_email.assert_not_called()

    def test_csv_encoding_is_unchanged(self):
        """Text attachments keep their MIMEText behavior."""
        path = Path(self.directory.name) / "data.csv"
        path.write_text("name,count\nalice,1\n")
        message = Message(["recipient@example.test"])
        message.attach_csv(str(path))
        part = message.get_payload()[0]
        self.assertEqual(part.get_content_type(), "text/csv")
        self.assertEqual(len(part.get_all("Content-Transfer-Encoding")), 1)
        self.assertEqual(part.get_payload(decode=True), path.read_bytes())


if __name__ == "__main__":
    unittest.main()
