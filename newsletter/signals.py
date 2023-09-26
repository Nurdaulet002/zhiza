# from django.db.models.signals import post_save
# from django.dispatch import receiver
#
# from newsletter.apscheduler import schedule_my_job
# from newsletter.models import Newsletter
#
#
# @receiver(post_save, sender=Newsletter)
# def my_model_post_save(sender, instance, created, **kwargs):
#     if created:
#         pass
#     else:
#         if instance.status == 5:
#             print('status is', instance.status)
#             schedule_my_job(newsletter=instance)
#         else:
#             pass
