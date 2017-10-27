from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_Account(sender, instance, created, **kwargs):
    if created:
        from account.models.commision_models import Account, Commision, AgentCommision
        Account.objects.create( user=instance )
        Commision.objects.create(user=instance )
        AgentCommision.objects.create(user=instance)
