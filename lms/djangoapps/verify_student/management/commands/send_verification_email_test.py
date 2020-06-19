"""
Django admin command to send verification approved email to learners
"""

import logging
import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from verify_student.utils import send_verification_confirmation_email, send_verification_approved_email

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    This command sends email to learner for which the Software Secure Photo Verification has approved

    Example usage:
        $ ./manage.py lms send_verification_email_test --username=staff --method=approved
        OR
        $ ./manage.py lms send_verification_email_test --username=staff --method=submitted
    """
    help = 'Send email to users for which Software Secure Photo Verification has expired'

    def add_arguments(self, parser):
        parser.add_argument('--username', help="The learner's email address or integer ID.")
        parser.add_argument('--method', required=True, help="Choose email method. `approved` or `submitted`")

    def handle(self, *args, **options):
        """
        Handler for the command

        It creates batches of expired Software Secure Photo Verification and sends it to send_verification_expiry_email
        that used edx_ace to send email to these learners
        """
        method = options['method']
        username = options['username']
        user = User.objects.get(username=username)
        context = {'user_id': user.id}

        if method == 'approved':
            logger.info('1. Trying to send ID verification approved email to user: {}'.format(username))
            expiry_date = datetime.date.today() + datetime.timedelta(
                days=settings.VERIFY_STUDENT["DAYS_GOOD_FOR"]
            )
            context['expiry_date'] = expiry_date.strftime("%m/%d/%Y")
            email_was_successful = send_verification_approved_email(context)
            logger.info('2. Email sending to user: {}, success: {}'.format(username, email_was_successful))

        else:
            logger.info('1. Trying to send ID verification submission confirmation email to user: {}'.format(username))
            email_was_successful = send_verification_confirmation_email(context)
            logger.info('2. Email sending to user: {}, success: {}'.format(username, email_was_successful))

