# from django.apps import AppConfig


# class MaintainResumeConfig(AppConfig):
#     name = 'maintain_resume'
from django.apps import AppConfig

class MaintainResumeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'maintain_resume'

    def ready(self):
        import maintain_resume.signals