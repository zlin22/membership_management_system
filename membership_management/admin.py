from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import MemberCreationForm, MemberChangeForm
from .models import Membership, Member, CheckInLog, Payment, AuxiliaryMember
from import_export.admin import ImportExportActionModelAdmin


# Register your models here.
class AuxiliaryMemberInline(admin.TabularInline):
    model = AuxiliaryMember
    extra = 1


class AuxiliaryMemberAdmin(admin.ModelAdmin):
    search_fields = ('email', 'first_name', 'last_name', 'primary_member')
    list_display = ('email', 'first_name', 'last_name',
                    'phone_number', 'primary_member', 'created_at')
    ordering = ('first_name', )
    readonly_fields = ('created_at', )


class MemberAdmin(UserAdmin):
    add_form = MemberCreationForm
    form = MemberChangeForm
    model = Member
    list_display = ('email', 'first_name', 'last_name',
                    'phone_number', 'membership', 'membership_expiration', 'created_at', )
    list_filter = ('is_staff',)
    # exclude = ('username',)
    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name', 'phone_number', 'profile_pic', 'membership',
                           'membership_expiration', 'stripe_subscription_id', 'stripe_customer_id',
                           'password', 'created_at')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    inlines = [
        AuxiliaryMemberInline
    ]
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'membership', 'membership_expiration', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('first_name', )
    readonly_fields = ('stripe_subscription_id', 'created_at', )


class PaymentAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('member', 'membership', 'amount', 'created_at', 'status')
    list_filter = ('status',)
    search_fields = ('amount', 'member__email')

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CheckInLogAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'checked_in_at')


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'is_displayed', 'is_subscription', 'display_order', )
    ordering = ('display_order', )
    list_filter = ('is_displayed', 'is_subscription', )


admin.site.register(Member, MemberAdmin)
admin.site.register(CheckInLog, CheckInLogAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(AuxiliaryMember, AuxiliaryMemberAdmin)
