"""
Default settings for the ``mezzanine_agenda`` app. Each of these can be
overridden in your project's settings module, just like regular
Django settings. The ``editable`` argument for each controls whether
the setting is editable via Django's admin.

Thought should be given to how a setting is actually used before
making it editable, as it may be inappropriate - for example settings
that are only read during startup shouldn't be editable, since changing
them would require an application reload.
"""
from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import register_setting


register_setting(
    name="ADMIN_MENU_ORDER",
    description=_("Controls the ordering and grouping of the admin menu."),
    editable=False,
    default=(
        (_("Content"), ("pages.Page", "blog.BlogPost", "mezzanine_agenda.Event",
            "generic.ThreadedComment", (_("Media Library"), "fb_browse"),)),
        (_("Site"), ("sites.Site", "redirects.Redirect", "conf.Setting")),
        (_("Users"), ("auth.User", "auth.Group",)),
    ),
)

register_setting(
    name="EVENT_USE_FEATURED_IMAGE",
    description=_("Enable featured images in events"),
    editable=False,
    default=False,
)

register_setting(
    name="EVENT_URLS_DATE_FORMAT",
    label=_("Event URL date format"),
    description=_("A string containing the value ``year``, ``month``, or "
        "``day``, which controls the granularity of the date portion in the "
        "URL for each event. Eg: ``year`` will define URLs in the format "
        "/events/yyyy/slug/, while ``day`` will define URLs with the format "
        "/events/yyyy/mm/dd/slug/. An empty string means the URLs will only "
        "use the slug, and not contain any portion of the date at all."),
    editable=False,
    default="",
)

register_setting(
    name="EVENT_PER_PAGE",
    label=_("Events per page"),
    description=_("Number of events shown on a event listing page."),
    editable=True,
    default=5,
)

register_setting(
    name="EVENT_RSS_LIMIT",
    label=_("Events RSS limit"),
    description=_("Number of most recent events shown in the RSS feed. "
        "Set to ``None`` to display all events in the RSS feed."),
    editable=False,
    default=20,
)

register_setting(
    name="EVENT_SLUG",
    description=_("Slug of the page object for the events."),
    editable=False,
    default="events",
)

register_setting(
    name="EVENT_GOOGLE_MAPS_DOMAIN",
    description="The Google Maps country domain to geocode addresses with",
    editable=True,
    default="maps.google.com",
)

register_setting(
    name="EVENT_TIME_ZONE",
    description="The timezone that event times are written in, if different from the timezone in settings.TIME_ZONE",
    editable=True,
    default="",
)

register_setting(
    name="EVENT_HIDPI_STATIC_MAPS",
    description="Generate maps suitable for Retina displays",
    editable=True,
    default=True,
)