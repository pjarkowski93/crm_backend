from typing import List, Optional

from crm.models import Files
from django.conf import settings
from django.core.mail import EmailMessage


class EmailSender:
    def send(
        self,
        recipient: str,
        message: str,
        subject: str,
        files: Optional[List[Files]] = [],
    ):
        mail = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[recipient],
        )
        for file in files:
            mail.attach_file(file.path_to_file)
        mail.send()
