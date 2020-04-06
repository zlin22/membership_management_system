from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from .managers import CustomUserManager

# Create your models here.


class Membership(models.Model):
    IS_SUBSCRIPTION_CHOICES = [
        ('Y', 'Yes'),
        ('N', 'No'),
    ]

    title = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=200, null=True)
    banner_message = models.CharField(max_length=100, null=True, blank=True)
    is_subscription = models.CharField(choices=IS_SUBSCRIPTION_CHOICES, max_length=1, null=True, default='N')
    subscription_plan_id = models.CharField(max_length=1000, blank=True, null=True, verbose_name="[ONLY for SUBSCRIPTIONS] plan ID in Stripe dashboard")
    number_of_days_valid = models.IntegerField(default=0, verbose_name="[ONLY for ONE-TIME memberships] number of days valid")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_displayed = models.BooleanField(verbose_name="Is displayed on the website for customer to purchase", default=True)
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
    membership = models.ForeignKey(Membership, on_delete=models.PROTECT, related_name="members", null=True, blank=True)
    membership_expiration = models.DateField(null=True, blank=True)
    override_recurring_cycle_starts_on = models.DateField(blank=True, null=True, verbose_name="Override recurring cycle start date (ONLY for recurring memberships)")
    stripe_subscription_id = models.CharField(max_length=500, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=500, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name',]

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class CheckInLog(models.Model):
    member = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name="check_in_logs")
    checked_in_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member} check in at {self.checked_in_at}"


class Payment(models.Model):
    member = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name="payments")
    membership = models.ForeignKey(Membership, on_delete=models.DO_NOTHING, related_name='payments', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_processor_id = models.CharField(max_length=1000, null=True, blank=True)
    status = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.member}'s ${self.amount} payment at {self.created_at}"
