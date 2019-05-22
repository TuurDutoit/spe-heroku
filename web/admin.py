from django.contrib import admin
from web.models import User, DandBcompany, Account, Contact, Lead, \
    Opportunity, Calendar, Event, Recommendation, Location, Route


class ReadOnlyModelAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class UserAdmin(ReadOnlyModelAdmin):
    list_display = ('name', 'username')
    list_select_related = ()


class DandBCompanyAdmin(ReadOnlyModelAdmin):
    list_display = ('name',)
    list_select_related = ()


class AccountAdmin(ReadOnlyModelAdmin):
    list_display = ('name', 'account_number', 'parent', 'owner')
    list_select_related = ()


class ContactAdmin(ReadOnlyModelAdmin):
    list_display = ('salutation', 'name', 'title')
    list_display_links = ('name',)
    list_select_related = ()


class LeadAdmin(ReadOnlyModelAdmin):
    list_display = ('salutation', 'name', 'status')
    list_display_links = ('name',)
    list_select_related = ()


class OpportunityAdmin(ReadOnlyModelAdmin):
    list_display = ('name', 'amount', 'close_date')
    list_select_related = ()


class CalendarAdmin(ReadOnlyModelAdmin):
    list_display = ('name', 'user', 'type')
    list_select_related = ()


class EventAdmin(ReadOnlyModelAdmin):
    list_display = ('subject', 'start_date_time',
                    'end_date_time', 'what', 'who')
    list_select_related = ()


class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('score', 'reason1', 'account_id', 'owner_id')


class LocationAdmin(admin.ModelAdmin):
    list_display = ('related_to', 'related_to_id', 'latitude', 'longitude')
    list_display_links = ('latitude', 'longitude')


class RouteAdmin(admin.ModelAdmin):
    list_display = ('start', 'end', 'distance')
    list_display_links = ('distance',)


admin.site.register(User, UserAdmin)
admin.site.register(DandBcompany, DandBCompanyAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Lead, LeadAdmin)
admin.site.register(Opportunity, OpportunityAdmin)
admin.site.register(Calendar, CalendarAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Recommendation, RecommendationAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Route, RouteAdmin)
