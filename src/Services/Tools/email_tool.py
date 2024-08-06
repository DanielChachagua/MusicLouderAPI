import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional

class MailTool:
    def __init__(self, smtp_server: str, port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password

    def send_email(
        self,
        subject: str,
        body: str,
        to_email: str,
        from_email: Optional[str] = None,
        attachments: Optional[list[str]] = None
    ) -> None:
        message = MIMEMultipart()
        message['From'] = from_email or self.username
        message['To'] = to_email
        message['Subject'] = subject

        message.attach(MIMEText(body, 'html'))

        if attachments:
            for file_path in attachments:
                try:
                    with open(file_path, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename={file_path.split("/")[-1]}',
                        )
                        message.attach(part)
                except FileNotFoundError:
                    print(f"El archivo {file_path} no se encuentra.")

        with smtplib.SMTP(self.smtp_server, self.port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(message)