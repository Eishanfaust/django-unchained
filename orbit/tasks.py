from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import CustomUser
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_birthday_wishes():
    """Send birthday wishes to users with birthday today"""
    try:
        birthday_users = CustomUser.objects.users_with_birthday_today()
        
        for user in birthday_users:
            if user.email:
                subject = f"Happy Birthday, {user.first_name or user.username}!"
                message = f"""
                Dear {user.first_name or user.username},

                Happy Birthday! 🎉

                Wishing you a wonderful day filled with happiness and joy.
                
                Best regards,
                The Backend Task Team
                """
                
                try:
                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False,
                    )
                    logger.info(f"Birthday wish sent to {user.email}")
                except Exception as e:
                    logger.error(f"Failed to send birthday wish to {user.email}: {e}")
        
        logger.info(f"Birthday wishes sent to {birthday_users.count()} users")
        return f"Birthday wishes sent to {birthday_users.count()} users"
    
    except Exception as e:
        logger.error(f"Error in send_birthday_wishes task: {e}")
        raise