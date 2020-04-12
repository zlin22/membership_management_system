from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import get_user_model, authenticate, login, logout, update_session_auth_hash
from .forms import MemberCreationForm
from .models import Membership, Member, CheckInLog, Payment
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.auth.forms import PasswordChangeForm
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db.models import Q

# START Stripe setup #############
# Set your secret key. Remember to switch to your live secret key in production!
# See your keys here: https://dashboard.stripe.com/account/apikeys
stripe.api_key = settings.STRIPE_API_KEY

# You can find your endpoint's secret in your webhook settings
endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

# checkout session success redirect URL
SUCCESS_URL = settings.STRIPE_REDIRECT_URL_BASE + '/account/update_success'

# checkout session cancel redirect URL
BUY_CANCEL_URL = settings.STRIPE_REDIRECT_URL_BASE + '/membership'
UPDATE_CANCEL_URL = settings.STRIPE_REDIRECT_URL_BASE + '/account'

# END Stripe setup ##########


def check_in(request):
    if request.method == "POST":
        try:
            email = request.POST["member_email"]
            member = get_user_model().objects.filter(Q(email__iexact=email) | Q(email__iexact=email)).first()
            try:
                is_membership_active = member.membership_expiration >= date.today()
            except Exception:
                is_membership_active = False

            if is_membership_active:
                context = {
                    "message1": f"{member.first_name} {member.last_name}!",
                    "message2": f"Your currently have an active membership",
                    "message3": f"It expires on {member.membership_expiration}",
                    "is_membership_active": is_membership_active,
                    "member": member,
                }
            else:
                context = {
                    "message1": f"{member.first_name} {member.last_name}!",
                    "message2": f"Your membership is NOT ACTIVE",
                    "message3": f"Please buy a new membership to play",
                    "purchase_button": True,
                    "is_membership_active": is_membership_active,
                    "member": member,
                }

            CheckInLog.objects.create(member=member)
            return render(request, "membership_management/check_in.html", context)

        except Exception:
            return render(request, "membership_management/check_in.html", {"message1": "No account found with that email. Please try again."})

    return render(request, "membership_management/check_in.html")


def membership_page(request):
    memberships = Membership.objects.filter(is_displayed=True)
    try:
        member = get_user_model().objects.get(email__iexact=request.user.email)
        is_membership_active = request.user.membership_expiration >= date.today()
    except Exception:
        is_membership_active = False
        member = None

    context = {
        "memberships": memberships,
        "is_membership_active": is_membership_active,
        "member": member,
    }

    return render(request, "membership_management/membership_page.html", context)


def account(request):
    if not request.user.is_authenticated:
        return render(request, "membership_management/login.html")
    else:
        try:
            is_membership_active = (
                request.user.membership_expiration >= date.today())
        except Exception:
            is_membership_active = False

        return render(request, "membership_management/account.html", {"member": request.user, "is_membership_active": is_membership_active})


def account_update_success(request):
    if not request.user.is_authenticated:
        return render(request, "membership_management/login.html")
    else:
        try:
            is_membership_active = (
                request.user.membership_expiration >= date.today())
        except Exception:
            is_membership_active = False

        context = {
            "member": request.user,
            "is_membership_active": is_membership_active,
            "message": "Your account is updated!"
        }

        return render(request, "membership_management/account.html", context)


def account_update_fail(request):
    if not request.user.is_authenticated:
        return render(request, "membership_management/login.html")
    else:
        try:
            is_membership_active = (
                request.user.membership_expiration >= date.today())
        except Exception:
            is_membership_active = False

        context = {
            "member": request.user,
            "is_membership_active": is_membership_active,
            "message": "Your account could not be updated."
        }

        return render(request, "membership_management/account.html", context)


def login_view(request):
    email = request.POST.get("email")
    password = request.POST.get("password")
    member = authenticate(request, email=email, password=password)

    if member is not None:
        login(request, member)
        return HttpResponseRedirect(reverse("account"))

    return render(request, "membership_management/login.html", {"message": "Invalid email/password."})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("account"))


def update_member(request):
    if request.method == "POST" and request.user.is_authenticated:
        member = get_user_model().objects.get(email__iexact=request.user.email)

        # return render(request, "membership_management/account.html", {"member": member, "message": "Information updated"})

        try:
            email = request.POST["email"]
            # first_name = request.POST["first_name"]
            # last_name = request.POST["last_name"]
            phone_number = request.POST["phone_number"]
            member.email = email
            # member.first_name = first_name
            # member.last_name = last_name
            member.phone_number = phone_number
            member.save()
            return render(request, "membership_management/account.html", {"member": member, "message": "Information updated"})
        except Exception:
            return render(request, "membership_management/account.html", {"member": member, "message": "Update error"})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('account')

    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'membership_management/change_password.html', {
        'form': form
    })


def create_account(request):
    if request.method == "POST":
        form = MemberCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            login(request, user)
            return redirect('account')
        else:
            # form = MemberCreationForm()
            return render(request, 'membership_management/create_account.html', {'form': form})

    else:
        return render(request, 'membership_management/create_account.html', {'form': MemberCreationForm()})


def stripe_create_session(request, membership_id):
    if request.method == "POST":
        try:
            selected_membership = Membership.objects.get(pk=int(membership_id))
        except Exception:
            return HttpResponseRedirect(reverse("membership_page"))

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'name': selected_membership.title,
                'description': selected_membership.description,
                'images': ['https://images.squarespace-cdn.com/content/v1/592715679de4bb56b6f52dc3/1575487314377-8ILD99MIL70XF02VY8V6/ke17ZwdGBToddI8pDm48kBD2FKG2VYgv9vJ-sxRHyeVZw-zPPgdn4jUwVcJE1ZvWhcwhEtWJXoshNdA9f1qD7eYzOKsynbf6SIIjIVpddg9XuI9fW4HahfJRw8_j4CZzf8pmB28R7ZtB-Q9IQS1W4w/favicon.ico'],
                # json.loads(request.body)['amount'],
                'amount': int(selected_membership.price * 100),
                'currency': 'usd',
                'quantity': 1,
            }],
            client_reference_id=selected_membership.title,
            success_url=SUCCESS_URL,
            cancel_url=BUY_CANCEL_URL,
            customer_email=request.user.email,
        )

        Payment.objects.create(member=request.user, membership=selected_membership,
                               amount=selected_membership.price, payment_processor_id=session['id'], status='pending')

        return JsonResponse(session)


def stripe_subscription_create_session(request, membership_id):
    if request.method == "POST":
        try:
            selected_membership = Membership.objects.get(pk=int(membership_id))
        except Exception:
            return HttpResponseRedirect(reverse("membership_page"))

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            subscription_data={
                'items': [{
                    'plan': selected_membership.subscription_plan_id,
                }],
            },
            success_url=SUCCESS_URL,
            cancel_url=BUY_CANCEL_URL,
            client_reference_id=selected_membership.title,
            customer_email=request.user.email,
        )

        Payment.objects.create(member=request.user, membership=selected_membership,
                               amount=selected_membership.price, payment_processor_id=session['id'], status='pending')

        return JsonResponse(session)


def stripe_get_session(request):
    session = stripe.checkout.Session.retrieve(
        request.GET['id']
    )
    return JsonResponse(session)


@csrf_exempt
def stripe_webhooks(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # print(session)

        # If webhook was from a payment purchase, update payments table with 'paid'
        # and extend membership date
        try:
            payment = Payment.objects.get(payment_processor_id=session['id'])
            payment.status = 'paid'
            payment.save()
            print('updated membership payment table')

            member = Member.objects.get(payments=payment.id)
            member.membership = payment.membership

            if member.membership_expiration is None:
                member.membership_expiration = date.today() + timedelta(days=-1)

            if session['subscription'] is None:
                member.membership_expiration = max([date.today(
                ) + timedelta(days=-1), member.membership_expiration]) + timedelta(days=(payment.membership.number_of_days_valid))
                member.save()
                print('no sub')
            else:
                subscription_interval = session['display_items'][0]['plan']['interval']
                if subscription_interval == 'month':
                    member.membership_expiration = max(
                        [date.today(), member.membership_expiration]) + relativedelta(months=1)

                member.stripe_subscription_id = session['subscription']
                member.stripe_customer_id = session['customer']
                member.save()
                print('sub')

        except Exception:
            print('no matching payment session from webhook')

        # If webhook was from a credit card update, get setup_intent
        try:
            # get setup intent which contains customer, subscription_id, and payment_method
            setup_intent = stripe.SetupIntent.retrieve(session['setup_intent'])
            print(setup_intent)

            # update customer's default payment method
            customer = setup_intent['customer']
            payment_method = setup_intent['payment_method']
            stripe.Customer.modify(
                customer,
                invoice_settings={'default_payment_method': payment_method}
            )

            # # update subscription's default payment method. alternate methodology will not impact default payment method
            # subscription_id = setup_intent['metadata']['subscription_id']
            # stripe.Subscription.modify(subscription_id, default_payment_method=payment_method)

        except Exception:
            print('no setup intent')

    if event['type'] == 'customer.subscription.updated':
        print('sub updated')

    return HttpResponse(status=200)


# update customer's credit card
def stripe_subscription_setup_session(request):
    try:
        subscription_id = request.user.stripe_subscription_id
        print('request.user.stripe_subscription_id')
        if subscription_id is None:
            return HttpResponse(status=404)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='setup',
            setup_intent_data={
                'metadata': {
                    'subscription_id': subscription_id,
                },
            },
            success_url=SUCCESS_URL,
            cancel_url=UPDATE_CANCEL_URL,
            customer=request.user.stripe_customer_id,
        )
        return JsonResponse(session)

    except Exception:
        return HttpResponse(status=400)


# cancel membership
def cancel_membership(request):
    try:
        stripe.Subscription.delete(request.user.stripe_subscription_id)
        member = get_user_model().objects.get(email__iexact=request.user.email)
        member.membership = None
        member.membership_expiration = date.today() + timedelta(days=-1)
        member.save()
        return HttpResponseRedirect(reverse("account_update_success"))
    except Exception:
        return HttpResponseRedirect(reverse("account_update_fail"))


# to do:
# forgot password - email server
# process membership renewal webhook
# process membership billing cycle update webhook
# family account
# admin panel QOL - export payments to csv, add filters to payments
# notify membership renewal failed payment
# email receipts for purchases
# email reminders when membership expires?
# auto log out
