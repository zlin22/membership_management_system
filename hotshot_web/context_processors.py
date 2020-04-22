from django.conf import settings


def export_vars(request):
    data = {}
    data['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
    data['COMPANY_NAME'] = settings.COMPANY_NAME
    return data
