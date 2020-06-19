"""
Django admin command to send verification approved email to learners
"""

import logging
import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from verify_student.tasks import send_verification_approved_email

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    This command sends email to learner for which the Software Secure Photo Verification has approved

    Example usage:
        $ ./manage.py lms send_verification_approved_email --username=staff
    """
    help = 'Send email to users for which Software Secure Photo Verification has expired'

    def add_arguments(self, parser):
        parser.add_argument('--username', help="The learner's email address or integer ID.")

    def handle(self, *args, **options):
        """
        Handler for the command

        It creates batches of expired Software Secure Photo Verification and sends it to send_verification_expiry_email
        that used edx_ace to send email to these learners
        """
        username = options['username']
        logger.info('1. Trying to send ID verification approved email to user: {}'.format(username))
        user = User.objects.get(username=username)
        expiry_date = datetime.date.today() + datetime.timedelta(
            days=settings.VERIFY_STUDENT["DAYS_GOOD_FOR"]
        )
        task_id = send_verification_approved_email.delay(
            context={'user_id': user.id, 'expiry_date': expiry_date.strftime("%m/%d/%Y")})
        logger.info('2. Email sending to user: {}, task ID: {}'.format(username, task_id))
