from __future__ import unicode_literals

from copy import deepcopy

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from mezzanine_agenda.models import Event, EventLocation
from mezzanine.conf import settings
from mezzanine.core.admin import DisplayableAdmin, OwnableAdmin


event_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
event_fieldsets[0][1]["fields"].insert(1, ("start", "end"))
event_fieldsets[0][1]["fields"].insert(2, "location")
event_fieldsets[0][1]["fields"].insert(3, "facebook_event")
event_fieldsets[0][1]["fields"].extend(["content", "allow_comments"])
event_list_display = ["title", "user", "status", "admin_link"]
if settings.EVENT_USE_FEATURED_IMAGE:
    event_fieldsets[0][1]["fields"].insert(-2, "featured_image")
    event_list_display.insert(0, "admin_thumb")
event_fieldsets = list(event_fieldsets)
event_list_filter = deepcopy(DisplayableAdmin.list_filter) + ("location",)


class EventAdmin(DisplayableAdmin, OwnableAdmin):
    """
    Admin class for events.
    """

    fieldsets = event_fieldsets
    list_display = event_list_display
    list_filter = event_list_filter

    def save_form(self, request, form, change):
        """
        Super class ordering is important here - user must get saved first.
        """
        OwnableAdmin.save_form(self, request, form, change)
        return DisplayableAdmin.save_form(self, request, form, change)


class EventLocationAdmin(admin.ModelAdmin):
    """
    Admin class for event locations. Hides itself from the admin menu
    unless explicitly specified.
    """

    fieldsets = ((None, {"fields": ("title", "address", "mappable_location", "lat", "lon")}),)

    def in_menu(self):
        """
        Hide from the admin menu unless explicitly set in ``ADMIN_MENU_ORDER``.
        """
        for (name, items) in settings.ADMIN_MENU_ORDER:
            if "mezzanine_agenda.EventLocation" in items:
                return True
        return False


admin.site.register(Event, EventAdmin)
admin.site.register(EventLocation, EventLocationAdmin)
