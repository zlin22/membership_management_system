from . import views
from django.urls import path

urlpatterns = [
    path('', views.check_in, name="check_in"),
    path('membership', views.membership_page, name='membership_page'),
    path('account', views.account, name='account'),
    path('account/update_success', views.account_update_success, name='account_update_success'),
    path('account/update_fail', views.account_update_fail, name='account_update_fail'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('create_account', views.create_account, name='create_account'),
    path('update_member', views.update_member, name='update_member'),
    path('cancel_membership', views.cancel_membership, name='cancel_membership'),
    path('change_password', views.change_password, name='change_password'),
    path('stripe_get_session', views.stripe_get_session, name='stripe_get_session'),
    path('stripe_create_session/<str:membership_id>', views.stripe_create_session, name='stripe_create_session'),
    path('stripe_subscription_create_session/<str:membership_id>', views.stripe_subscription_create_session, name='stripe_subscription_create_session'),
    path('stripe_subscription_setup_session', views.stripe_subscription_setup_session, name='stripe_subscription_setup_session'),
    path('stripe_webhooks', views.stripe_webhooks, name='stripe_webhooks'),
]
