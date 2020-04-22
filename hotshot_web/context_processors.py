from django.conf import settings


def export_vars(request):
    data = {}
    data['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
    return data
