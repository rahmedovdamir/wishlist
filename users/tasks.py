from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_welcome_email(email, first_name):
    subject = "Добро пожаловать!"
    message = f"""
    Привет, {first_name},

    Спасибо, что присоединились к моему сайту! .
    Исследуйте  возможности wishlist и пользуйтесь с удобством.

    Если будут вопросы/пожелания пишите на эту почту!
    """
    html_message = f"""
    <h1>Добро пожаловать, {first_name}!</h1>
    <p>Спасибо, что присоединились к моему сайту! Мы рады видеть вас с нами.</p>
    <p>Исследуйте  возможности wishlist и пользуйтесь с удобством.</p>
    <p>Если будут вопросы/пожелания пишите на эту почту!</p>
    """
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
            html_message=html_message
        )
        logger.info(f"Приветственное письмо отправлено на {email}")
    except Exception as e:
        logger.error(f"Не удалось отправить приветственное письмо на {email}: {str(e)}")
        raise

@shared_task
def send_password_reset_email(email, user_id):
    from .models import CustomUser
    from django.urls import reverse
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes

    logger.info(f"Запуск задачи отправки письма для сброса пароля для {email}, user_id={user_id}")
    try:
        user = CustomUser.objects.get(pk=user_id)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.SITE_URL}{reverse('users:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"
        subject = "Запрос на сброс пароля"
        message = f"""
        Привет {user.first_name or user.email},

        Пожалуйста, перейдите по ссылке ниже, чтобы сбросить ваш пароль:
        {reset_url}

        Если вы не запрашивали сброс пароля, проигнорируйте это письмо.

        Если будут вопросы/пожелания пишите на эту почту!
        """
        html_message = f"""
        <h1>Запрос на сброс пароля</h1>
        <p>Привет {user.first_name or user.email},</p>
        <p>Пожалуйста, перейдите по ссылке ниже, чтобы сбросить ваш пароль:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>Если вы не запрашивали сброс пароля, проигнорируйте это письмо.</p>
        <p>Если будут вопросы/пожелания пишите на эту почту!</p>
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
            html_message=html_message
        )
        logger.info(f"Письмо для сброса пароля отправлено на {email}")
    except Exception as e:
        logger.error(f"Не удалось отправить письмо для сброса пароля на {email}: {str(e)}")
        raise