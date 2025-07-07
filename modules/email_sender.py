import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from utils.logger import setup_logging
import ssl

class EmailSender:
    """Class to send emails with attachments."""
    
    def __init__(self):
        self.logger = setup_logging('email_sender')
        self.context = ssl.create_default_context()
        
    def send_email(
        self,
        sender_email: str,
        sender_password: str,
        smtp_server: str,
        smtp_port: int,
        receiver_email: str,
        subject: str,
        body: str,
        attachments: list = None
    ) -> str:
        """
        Send an email with optional attachments.
        
        Args:
            sender_email: Sender's email address
            sender_password: Sender's email password
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            receiver_email: Recipient's email address
            subject: Email subject
            body: Email body text
            attachments: List of file paths to attach
            
        Returns:
            Status message
        """
        try:
            # Create message container
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    path = Path(file_path)
                    if path.exists():
                        with open(path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename={path.name}'
                        )
                        msg.attach(part)
            
            # Connect to SMTP server and send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.ehlo()
                server.starttls(context=self.context)
                server.ehlo()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            self.logger.info(f"Email sent successfully to {receiver_email}")
            return "Email sent successfully"
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return f"Error sending email: {str(e)}"