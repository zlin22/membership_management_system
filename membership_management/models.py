from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
# PublicMediaStorage can also be used
from hotshot_web.storage_backends import PrivateMediaStorage
from .managers import CustomUserManager
from django.utils.timezone import localtime


# Create your models here.
class Membership(models.Model):
    IS_SUBSCRIPTION_CHOICES = [
        ('Y', 'Yes'),
        ('N', 'No'),
    ]

    title = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=200, null=True)
    banner_message = models.CharField(max_length=100, null=True, blank=True)
    is_subscription = models.CharField(
        choices=IS_SUBSCRIPTION_CHOICES, max_length=1, null=True, default='N')
    subscription_plan_id = models.CharField(
        max_length=1000, blank=True, null=True, verbose_name="[ONLY for SUBSCRIPTIONS] price ID in Stripe dashboard")
    number_of_days_valid = models.IntegerField(
        default=0, verbose_name="[ONLY for ONE-TIME memberships] number of days valid")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_displayed = models.BooleanField(
        verbose_name="Is displayed for purchase", default=True)
    display_order = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.title}"


class Member(AbstractUser):
    username = None
    email = models.EmailField(_('Email address'), unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=16, blank=True)
    membership = models.ForeignKey(
        Membership, on_delete=models.PROTECT, related_name="members", null=True, blank=True)
    membership_expiration = models.DateField(null=True, blank=True)
    stripe_subscription_id = models.CharField(
        max_length=500, blank=True, null=True,)
    stripe_customer_id = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="[DO NOT EDIT UNLESS INSTRUCTED] Stripe customer ID")
    profile_pic = models.ImageField(
        upload_to='profile_pic', blank=True, null=True, storage=PrivateMediaStorage())
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', ]

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class AuxiliaryMember(models.Model):
    primary_member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="auxiliary_members")
    email = models.EmailField(_('Email address'), unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=16, blank=True)
    profile_pic = models.ImageField(
        upload_to='profile_pic', blank=True, null=True, storage=PrivateMediaStorage())
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.email


class CheckInLog(models.Model):
    email = models.EmailField(_('Email address'), null=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=16, blank=True)
    checked_in_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email}) checked in at {localtime(self.checked_in_at).strftime('%Y-%m-%d %I:%M:%S %p')}"


class Payment(models.Model):
    member = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, related_name="payments")
    membership = models.ForeignKey(
        Membership, on_delete=models.DO_NOTHING, related_name='payments', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_processor_id = models.CharField(
        max_length=1000, null=True, blank=True)
    status = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.member}'s ${self.amount} payment at {self.created_at}"
