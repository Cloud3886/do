import mimetypes
from abc import abstractmethod
from email.headerregistry import Address
from email.message import EmailMessage
from typing import Protocol, Sequence

RCPT = Address | str | Sequence[Address] | Sequence[str]


class EmailClient(Protocol):
    def send_email(
        self,
        to: RCPT,
        subject: str,
        body: str,
        *,
        subtype: str = "plain",
        sender: Address | str | None = None,
        cc: RCPT | None = None,
        bcc: RCPT | None = None,
    ):
        message = self.create_message(
            to,
            subject,
            body,
            subtype=subtype,
            sender=sender,
            cc=cc,
            bcc=bcc,
        )
        res = self._send_email(message)
        return res

    def send_email_with_attachments(
        self,
        to: RCPT,
        subject: str,
        body: str,
        attachment_paths: Sequence[str],
        *,
        subtype: str = "plain",
        sender: Address | str | None = None,
        cc: RCPT | None = None,
        bcc: RCPT | None = None,
    ):
        message = self.create_message(
            to,
            subject,
            body,
            subtype=subtype,
            sender=sender,
            cc=cc,
            bcc=bcc,
        )
        for attachment_path in attachment_paths:
            message = self.add_attachment(message, attachment_path)
        res = self._send_email(message)
        return res

    def draft_email(
        self,
        to: RCPT,
        subject: str,
        body: str,
        *,
        subtype: str = "plain",
        sender: Address | str | None = None,
        cc: RCPT | None = None,
        bcc: RCPT | None = None,
    ):
        message = self.create_message(
            to,
            subject,
            body,
            subtype=subtype,
            sender=sender,
            cc=cc,
            bcc=bcc,
        )
        res = self._draft_email(message)
        return res

    def create_message(
        self,
        to: RCPT,
        subject: str,
        body: str,
        *,
        subtype: str = "plain",
        sender: Address | str | None = None,
        cc: RCPT | None = None,
        bcc: RCPT | None = None,
    ) -> EmailMessage:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = sender  # type: ignore
        message["To"] = to  # type: ignore
        if cc:
            message["Cc"] = cc  # type: ignore
        if bcc:
            message["Bcc"] = bcc  # type: ignore
        message.set_content(body, subtype=subtype)
        return message

    def add_alternate_content(
        self,
        message: EmailMessage,
        body: str,
        subtype: str = "html",
    ) -> EmailMessage:
        message.add_alternative(body, subtype=subtype)
        return message

    def add_attachment(
        self,
        message: EmailMessage,
        attachment_file_path: str,
        file_name: str | None = None,
    ) -> EmailMessage:
        if not file_name:
            file_name = attachment_file_path.split("/")[-1]
            # file_name = file_name.rsplit(".", 1)[0]
        # Guess the content type based on the file's extension.  Encoding
        # will be ignored, although we should check for simple things like
        # gzip'd or compressed files.
        ctype, encoding = mimetypes.guess_type(attachment_file_path)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(attachment_file_path, "rb") as fp:
            attachment_data = fp.read()
        message.add_attachment(
            attachment_data,
            maintype=maintype,
            subtype=subtype,
            filename=file_name,
        )
        return message

    @abstractmethod
    def _send_email(self, message: EmailMessage):
        pass

    @abstractmethod
    def _draft_email(self, message: EmailMessage):
        pass
