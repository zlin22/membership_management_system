from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import get_user_model, authenticate, login, logout, update_session_auth_hash
from .forms import MemberCreationForm
from .models import Membership, Member, CheckInLog, Payment, AuxiliaryMember
from datetime import date, timedelta, datetime
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
    # if request is POST try to find the member information
    if request.method == "POST":
        email_or_phone = request.POST["email_or_phone"]

        # try to get email from submission; if fail, return no account found
        # first check if email belongs to primary user; set to member if found
        try:
            member = get_user_model().objects.get(
                Q(email__iexact=email_or_phone) | Q(
                    phone_number=email_or_phone)
            )

        except Exception:
            # check if email belongs to auxiliary member; set to member if found
            try:
                member = AuxiliaryMember.objects.get(
                    Q(email__iexact=email_or_phone) | Q(
                        phone_number=email_or_phone)
                )

            except Exception:
                context = {
                    "message2": "No account found. Please try again.",
                    "alert_type": "alert-warning",
                }
                return render(request, "membership_management/check_in.html", context)

        # try to get is_membership_active status; if not able, set is_membership_active to false
        try:
            is_membership_active = member.membership_expiration >= date.today()
            membership_expiration = member.membership_expiration
        except Exception:
            try:
                is_membership_active = member.primary_member.membership_expiration >= date.today()
                membership_expiration = member.primary_member.membership_expiration
            except Exception:
                is_membership_active = False

        if is_membership_active:
            context = {
                "message1": f"{member.first_name} {member.last_name}!",
                "message2": f"Your membership is ACTIVE.",
                "message3": f"It expires on {membership_expiration}",
                "profile_pic": member.profile_pic,
                "alert_type": "alert-success",
            }
        else:
            context = {
                "message1": f"{member.first_name} {member.last_name}!",
                "message2": f"Your membership is NOT ACTIVE.",
                "message3": f"",
                "purchase_button": True,
                "profile_pic": member.profile_pic,
                "alert_type": "alert-danger",
            }

        CheckInLog.objects.create(
            email=member.email, first_name=member.first_name,
            last_name=member.last_name, phone_number=member.phone_number
        )
        return render(request, "membership_management/check_in.html", context)

    # if request is GET display check in form
    else:
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

    context = {
        "member": request.user,
        "is_membership_active": is_membership_active,
    }

    return render(request, "membership_management/account.html", context)


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
            return render(request, 'membership_management/create_account.html', {'form': form})

    else:
        return render(request, 'membership_management/create_account.html', {'form': MemberCreationForm()})


# create stripe session for buying a one time item
def stripe_create_session(request, membership_id):
    if request.method == "POST":
        try:
            selected_membership = Membership.objects.get(pk=int(membership_id))
        except Exception:
            # return HttpResponseRedirect(reverse("membership_page"))
            return HttpResponse(status=400)

        # if the customer has a stripe customer id, include it in request
        if request.user.stripe_customer_id is None:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'name': selected_membership.title,
                    'description': selected_membership.description,
                    # 'images': ['https://images.squarespace-cdn.com/content/v1/592715679de4bb56b6f52dc3/1575487314377-8ILD99MIL70XF02VY8V6/ke17ZwdGBToddI8pDm48kBD2FKG2VYgv9vJ-sxRHyeVZw-zPPgdn4jUwVcJE1ZvWhcwhEtWJXoshNdA9f1qD7eYzOKsynbf6SIIjIVpddg9XuI9fW4HahfJRw8_j4CZzf8pmB28R7ZtB-Q9IQS1W4w/favicon.ico'],
                    # json.loads(request.body)['amount'],
                    'amount': int(selected_membership.price * 100),
                    'currency': 'usd',
                    'quantity': 1,
                }],
                client_reference_id=selected_membership.title,
                success_url=SUCCESS_URL,
                cancel_url=BUY_CANCEL_URL,
                customer_email=request.user.email,
                payment_intent_data={
                    'description': selected_membership.title,
                    'statement_descriptor': selected_membership.title
                },
            )

        else:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'name': selected_membership.title,
                    'description': selected_membership.description,
                    # 'images': ['https://images.squarespace-cdn.com/content/v1/592715679de4bb56b6f52dc3/1575487314377-8ILD99MIL70XF02VY8V6/ke17ZwdGBToddI8pDm48kBD2FKG2VYgv9vJ-sxRHyeVZw-zPPgdn4jUwVcJE1ZvWhcwhEtWJXoshNdA9f1qD7eYzOKsynbf6SIIjIVpddg9XuI9fW4HahfJRw8_j4CZzf8pmB28R7ZtB-Q9IQS1W4w/favicon.ico'],
                    # json.loads(request.body)['amount'],
                    'amount': int(selected_membership.price * 100),
                    'currency': 'usd',
                    'quantity': 1,
                }],
                client_reference_id=selected_membership.title,
                success_url=SUCCESS_URL,
                cancel_url=BUY_CANCEL_URL,
                customer=request.user.stripe_customer_id,
                payment_intent_data={
                    'description': selected_membership.title,
                    'statement_descriptor': selected_membership.title
                },
            )

        Payment.objects.create(member=request.user, membership=selected_membership,
                               amount=selected_membership.price, payment_processor_id=session['id'], status='pending')

        return JsonResponse(session)


# create stripe session for buying a subscription
def stripe_subscription_create_session(request, membership_id):
    if request.method == "POST":
        try:
            selected_membership = Membership.objects.get(pk=int(membership_id))
        except Exception:
            return HttpResponseRedirect(reverse("membership_page"))

        # if the customer has a stripe customer id, include it in request
        if request.user.stripe_customer_id is None:
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

        else:
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
                customer=request.user.stripe_customer_id,
            )

        Payment.objects.create(member=request.user, membership=selected_membership,
                               amount=selected_membership.price, payment_processor_id=session['id'], status='pending')

        return JsonResponse(session)


def stripe_get_session(request):
    session = stripe.checkout.Session.retrieve(
        request.GET['id']
    )
    return JsonResponse(session)


# update customer's credit card
def stripe_subscription_setup_session(request):
    try:
        subscription_id = request.user.stripe_subscription_id
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
        event_info = event['data']['object']
        # print(session)

        # If webhook was from a payment purchase, update payments table with 'paid'
        # and extend membership date
        try:
            # update payment table with status = paid
            payment = Payment.objects.get(
                payment_processor_id=event_info['id'])
            payment.status = 'paid'
            payment.save()

            # update membership with the membership that is paid
            member = Member.objects.get(payments=payment.id)
            member.membership = payment.membership

            if member.membership_expiration is None:
                member.membership_expiration = date.today() + timedelta(days=-1)

            # if the payment was for a one-time purchase, save stripe customer id, and update membership exp date
            if event_info['subscription'] is None:
                member.stripe_customer_id = event_info['customer']
                member.save()

                member.membership_expiration = max([date.today(
                ) + timedelta(days=-1), member.membership_expiration]) + timedelta(days=(payment.membership.number_of_days_valid))
                member.save()

            # if the payment was for a subscription, store stripe subscription id, customer id
            # and calculate expiration date
            else:
                subscription_interval = event_info['display_items'][0]['plan']['interval']
                if subscription_interval == 'month':
                    member.membership_expiration = max(
                        [date.today(), member.membership_expiration]) + relativedelta(months=1)

                member.stripe_subscription_id = event_info['subscription']
                member.stripe_customer_id = event_info['customer']
                member.save()

        except Exception:
            print('no matching payment session from webhook')

        # If webhook was from a credit card update, get setup_intent
        try:
            # get setup intent which contains customer, subscription_id, and payment_method
            setup_intent = stripe.SetupIntent.retrieve(
                event_info['setup_intent'])

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

    # process invoice.payment_succeed webhook
    # triggers once every subscription period when payment is successful
    # update membership plan, membership expiration date, subscription id
    if event['type'] == 'invoice.payment_succeeded':
        event_info = event['data']['object']

        # try to get member from webhook customer id
        try:
            # exctract data from webhook
            stripe_customer_id = event_info['customer']
            stripe_subscription_id = event_info['lines']['data'][0]['subscription']
            membership_expiration = datetime.fromtimestamp(
                event_info['lines']['data'][0]['period']['end'])
            subscription_plan_id = event_info['lines']['data'][0]['plan']['id']

            # update member info
            member = get_user_model().objects.get(stripe_customer_id=stripe_customer_id)
            member.stripe_subscription_id = stripe_subscription_id
            member.membership_expiration = membership_expiration
            membership = Membership.objects.get(
                subscription_plan_id=subscription_plan_id)
            member.membership = membership
            member.save()
            print('member exp updated')

        except Exception:
            print('could not update member exp')

        print('invoice paid')

    # process customer.subscription.updated webhook
    # triggers when subscription is updated on stripe (ie. when adding a trial period to subscription)
    # update membership plan, membership expiration date, subscription id
    if event['type'] == 'customer.subscription.updated':
        event_info = event['data']['object']

        # try to get member from webhook customer id
        try:
            # exctract data from webhook
            stripe_customer_id = event_info['customer']
            stripe_subscription_id = event_info['id']
            membership_expiration = datetime.fromtimestamp(
                event_info['current_period_end'])
            subscription_plan_id = event_info['plan']['id']
            cancel_at_date = event_info['cancel_at']

            # update member info
            member = get_user_model().objects.get(stripe_customer_id=stripe_customer_id)
            member.stripe_subscription_id = stripe_subscription_id
            member.membership_expiration = membership_expiration
            if cancel_at_date is None:
                membership = Membership.objects.get(
                    subscription_plan_id=subscription_plan_id)
            else:
                membership = None
            member.membership = membership
            member.save()
            print('subscription updated')

        except Exception:
            print('could not update subcription')

    # process customer.subscription.deleted webhook
    # triggers when subscription is canceled on stripe
    # update membership plan, membership expiration date, subscription id
    if event['type'] == 'customer.subscription.deleted':
        event_info = event['data']['object']

        # try to get member from webhook customer id
        try:
            # exctract data from webhook
            stripe_customer_id = event_info['customer']
            cancel_at_period_end = event_info['cancel_at_period_end']
            if cancel_at_period_end is True:
                membership_expiration = datetime.fromtimestamp(
                    event_info['current_period_end'])
            else:
                membership_expiration = date.today() + timedelta(days=-1)

            # update member info
            member = get_user_model().objects.get(stripe_customer_id=stripe_customer_id)
            member.stripe_subscription_id = None
            member.membership_expiration = membership_expiration
            member.membership = None
            member.save()

        except Exception:
            print('could not cancel subcription')

    return HttpResponse(status=200)
