from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView
from django.contrib.auth import get_user_model, authenticate, login, logout, update_session_auth_hash, password_validation
from .forms import MemberCreationForm
from .models import Membership, Member, CheckInLog, Payment
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.auth.forms import PasswordChangeForm
import uuid
import stripe
import json
from django.views.decorators.csrf import csrf_exempt


# Create your views here.


def check_in(request):
    if request.method == "POST":
        try:
            email = request.POST["member_email"]
            member = get_user_model().objects.get(email=email)

            if (member.membership_expiration is not None) and (member.membership_expiration >= date.today()):
                context = {
                    "message1": f"Welcome {member.first_name}!",
                    "message2": f"Your currently have an active {member.membership}",
                    "message3": f"It expires on {member.membership_expiration}"
                }
            else:
                context = {
                    "message1": f"Welcome {member.first_name}!",
                    "message2": f"Your membership is NOT ACTIVE",
                    "message3": f"Please buy a new membership to play",
                    "purchase_button": True,
                }

            CheckInLog.objects.create(member=member)
            return render(request, "membership_management/check_in.html", context)

        except:
            return render(request, "membership_management/check_in.html", {"message1": "Invald email. Please try again."})

    return render(request, "membership_management/check_in.html")


def membership_page(request):
    memberships = Membership.objects.filter(is_displayed=True)
    return render(request, "membership_management/membership_page.html", {"memberships": memberships})


def account(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return render(request, "membership_management/login.html")
        else:
            try:
                is_membership_active = (request.user.membership_expiration >= date.today())
            except:
                is_membership_active = False
                
            return render(request, "membership_management/account.html", {"member": request.user, "is_membership_active": is_membership_active})


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
        member = get_user_model().objects.get(email=request.user.email)

        try:
            email = request.POST["email"]
            first_name = request.POST["first_name"]
            last_name = request.POST["last_name"]
            phone_number = request.POST["phone_number"]
            member.email = email
            member.first_name = first_name
            member.last_name = last_name
            member.phone_number = phone_number
            member.save()
            return render(request, "membership_management/account.html", {"member": member, "message": "Information updated"})
        except:
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


# def subscribe(request, membership_id):
#     try:
#         selected_membership = Membership.objects.get(pk=membership_id)
#         context = {"membership": selected_membership}
#     except:
#         return HttpResponseRedirect(reverse("membership_page"))

#     if not request.user.is_authenticated:
#         return render(request, "membership_management/login.html")

#     context.update({"member": request.user})

#     if request.method == "POST":
#         # Create an instance of the API Client
#         # and initialize it with the credentials
#         # for the Square account whose assets you want to manage

#         client = Client(
#             access_token='EAAAEDjhGlYSsPaPl8t01AzkGgY9nKZoI-z8vuqX8oSHXsQJ4O7qK6jGC2LudLpg',
#             environment='sandbox',
#         )

#         # Get an instance of the Square API you want call
#         payments_api = client.payments

#         # Call list_locations method to get all locations in this Square account
#         # result = api_locations.list_locations()

#         cents_charged = int(selected_membership.price * 100)
#         nonce = request.POST["nonce"]

#         body = {
#             "source_id": nonce,
#             "idempotency_key": str(uuid.uuid1()),
#             "amount_money": {"amount": cents_charged, "currency": "USD"}
#         }

#         payment_results = payments_api.create_payment(body)

#         # Call the success method to see if the call succeeded
#         if payment_results.is_success():
#             # The body property is a list of locations
#             response = payment_results.body['payment']
#             # Iterate over the list
#             # print(context)

#             # update the member's membership

#             order_pk = {
#                 "order_message": "Your order has been placed!",
#                 # "grand_total": current_order.grand_total,
#                 # "order_pk": current_order.id,
#             }

#             response.update(order_pk)

#             return JsonResponse(response)

#         # Call the error method to see if the call failed
#         elif payment_results.is_error():
#             print('Error calling payment API')
#             context = payment_results.errors
#             errors = payment_results.errors
#             # An error is returned as a list of errors
#             # for error in errors:
#             #     # Each error is represented as a dictionary
#             #     for key, value in error.items():
#             #         print(f"{key} : {value}")
#             #     print("\n")
#             print(errors)

#     return render(request, "membership_management/subscribe.html", context)


def stripe_create_session(request, membership_id):
    if request.method == "POST":
        try:
            selected_membership = Membership.objects.get(pk=int(membership_id))
        except:
            return HttpResponseRedirect(reverse("membership_page"))

        # Set your secret key. Remember to switch to your live secret key in production!
        # See your keys here: https://dashboard.stripe.com/account/apikeys
        stripe.api_key = 'sk_test_SWwTfJnmN1RP1IzSfABCb1Gb006CDUoL74'

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
            success_url='http://127.0.0.1:8000/account?id={CHECKOUT_SESSION_ID}',
            cancel_url='http://127.0.0.1:8000/membership',
            customer_email=request.user.email,
        )

        Payment.objects.create(member=request.user, membership=selected_membership,
                               amount=selected_membership.price, payment_processor_id=session['id'], status='pending')

        return JsonResponse(session)


def stripe_subscription_create_session(request, membership_id):
    if request.method == "POST":
        try:
            selected_membership = Membership.objects.get(pk=int(membership_id))
        except:
            return HttpResponseRedirect(reverse("membership_page"))

        # Set your secret key. Remember to switch to your live secret key in production!
        # See your keys here: https://dashboard.stripe.com/account/apikeys
        stripe.api_key = 'sk_test_SWwTfJnmN1RP1IzSfABCb1Gb006CDUoL74'

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            subscription_data={
                'items': [{
                    'plan': selected_membership.subscription_plan_id,
                }],
            },
            success_url='http://127.0.0.1:8000/account?id={CHECKOUT_SESSION_ID}',
            cancel_url='http://127.0.0.1:8000/membership',
            client_reference_id=selected_membership.title,
            customer_email=request.user.email,
        )

        Payment.objects.create(member=request.user, membership=selected_membership,
                               amount=selected_membership.price, payment_processor_id=session['id'], status='pending')

        return JsonResponse(session)


def stripe_get_session(request):
    stripe.api_key = 'sk_test_SWwTfJnmN1RP1IzSfABCb1Gb006CDUoL74'

    session = stripe.checkout.Session.retrieve(
        request.GET['id']
    )
    return JsonResponse(session)


# Set your secret key. Remember to switch to your live secret key in production!
# See your keys here: https://dashboard.stripe.com/account/apikeys
stripe.api_key = 'sk_test_SWwTfJnmN1RP1IzSfABCb1Gb006CDUoL74'

# Using Django

# You can find your endpoint's secret in your webhook settings
endpoint_secret = 'whsec_0hCUifwGvACRspd3zGLk0aDhqJRhxASu'


@csrf_exempt
def stripe_webhooks(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Update payments table with 'paid'
        payment = Payment.objects.get(payment_processor_id=session['id'])
        payment.status = 'paid'
        payment.save()
        print('updated membership payment table')

        member = Member.objects.get(payments=payment.id)
        member.membership = payment.membership

        if session['subscription'] is None:
            member.membership_expiration = max([date.today(
            ) + timedelta(days=-1), member.membership_expiration]) + timedelta(days=(payment.membership.number_of_days_valid))
            member.save()
            print('no sub')
        else:
            subscription_interval = session['display_items'][0]['plan']['interval']
            if subscription_interval == 'month':
                member.membership_expiration = date.today() + relativedelta(months=1)

            member.stripe_subscription_id = session['subscription']
            member.stripe_customer_id = session['customer']
            member.save()
            print('sub')

    if event['type'] == 'customer.subscription.updated':
        print('sub updated')

    return HttpResponse(status=200)


# to do:
# cancel membership
# update membership credit card
# process membership renewal webhook
# process membership billing cycle update webhook
# buying memberships when member already have an active recurring membership
# forgot password
# email receipts for purchases
# admin panel QOL
# env variables setup
