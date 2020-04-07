from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import MemberCreationForm, MemberChangeForm
from .models import Membership, Member, CheckInLog, Payment

# Register your models here.


class MemberAdmin(UserAdmin):
    add_form = MemberCreationForm
    form = MemberChangeForm
    model = Member
    list_display = ('email', 'first_name', 'last_name',
                    'phone_number', 'membership', 'membership_expiration', )
    list_filter = ('is_staff',)
    # exclude = ('username',)
    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name', 'phone_number', 'membership',
                           'membership_expiration', 'stripe_subscription_id', 'stripe_customer_id',
                           'override_recurring_cycle_starts_on', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'membership', 'membership_expiration', 'override_recurring_cycle_starts_on', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('first_name', )
    readonly_fields = ('stripe_subscription_id', 'stripe_customer_id')

    # def _allow_edit(self, obj=None):
    #     if not obj:
    #         return True
    #     return not (obj.is_staff or obj.is_superuser)

    # def has_change_permission(self, request, obj=None):
    #     return self._allow_edit(obj)

    # def has_delete_permission(self, request, obj=None):
    #     return self._allow_edit(obj)

    def has_add_permission(self, request):
        return True

    def has_view_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True


class CheckInLogAdmin(admin.ModelAdmin):
    list_display = ('member', 'checked_in_at')
    readonly_fields = ('member', 'checked_in_at')


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('member', 'membership', 'amount', 'created_at', 'status')

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Member, MemberAdmin)
admin.site.register(CheckInLog, CheckInLogAdmin)
admin.site.register(Membership)
admin.site.register(Payment, PaymentAdmin)
