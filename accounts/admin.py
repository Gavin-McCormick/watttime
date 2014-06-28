from accounts.models import UserProfile, ca_model, ne_model
from django.contrib import admin


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'state', 'phone', 'password_is_set', 'is_verified', 'ca_settings', 'ne_settings')
    list_filter = ('state', 'password_is_set', 'is_verified')
    readonly_fields = ('magic_login_code', 'verification_code')


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    extra = 1
    readonly_fields = ('magic_login_code', 'verification_code', 'ca_settings', 'ne_settings', 'null_settings')


class CASettingsAdmin(admin.ModelAdmin):
    list_display = ('message_frequency', 'forecast_email')
    list_filter = ('message_frequency', 'forecast_email')
    inlines = [UserProfileInline]


class NESettingsAdmin(admin.ModelAdmin):
    list_display = ('message_frequency',)
    list_filter = ('message_frequency',)
    inlines = [UserProfileInline]


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(ca_model, CASettingsAdmin)
admin.site.register(ne_model, NESettingsAdmin)
