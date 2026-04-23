from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import os


@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    if os.environ.get("CREATE_SUPERUSER") == "True":
        User = get_user_model()

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if username and password and not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)