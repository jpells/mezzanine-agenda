from __future__ import unicode_literals

from django.conf.urls import patterns, url

from mezzanine.conf import settings


# Trailing slash for urlpatterns based on setup.
_slash = "/" if settings.APPEND_SLASH else ""

# Agenda patterns.
urlpatterns = patterns("mezzanine_agenda.views",
    url("^feeds/(?P<format>.*)%s$" % _slash,
        "event_feed", name="event_feed"),
    url("^tag/(?P<tag>.*)/feeds/(?P<format>.*)%s$" % _slash,
        "event_feed", name="event_feed_tag"),
    url("^tag/(?P<tag>.*)%s$" % _slash, "event_list",
        name="event_list_tag"),
    url("^tag/(?P<tag>.*)/calendar.ics$", "icalendar",
        name="icalendar_tag"),
    url("^location/(?P<location>.*)/feeds/(?P<format>.*)%s$" % _slash,
        "event_feed", name="event_feed_location"),
    url("^location/(?P<location>.*)%s$" % _slash,
        "event_list", name="event_list_location"),
    url("^location/(?P<location>.*)/calendar.ics$",
        "icalendar", name="icalendar_location"),
    url("^author/(?P<username>.*)/feeds/(?P<format>.*)%s$" % _slash,
        "event_feed", name="event_feed_author"),
    url("^author/(?P<username>.*)%s$" % _slash,
        "event_list", name="event_list_author"),
    url("^author/(?P<username>.*)/calendar.ics$",
        "icalendar", name="icalendar_author"),
    url("^archive/(?P<year>\d{4})/(?P<month>\d{1,2})%s$" % _slash,
        "event_list", name="event_list_month"),
    url("^archive/(?P<year>\d{4})/(?P<month>\d{1,2})/calendar.ics$",
        "icalendar", name="icalendar_month"),
    url("^archive/(?P<year>\d{4})%s$" % _slash,
        "event_list", name="event_list_year"),
    url("^archive/(?P<year>\d{4})/calendar.ics$",
        "icalendar", name="icalendar_year"),
    url("^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/"
        "(?P<slug>.*)%s$" % _slash,
        "event_detail", name="event_detail_day"),
    url("^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>.*)%s$" % _slash,
        "event_detail", name="event_detail_month"),
    url("^(?P<year>\d{4})/(?P<slug>.*)%s$" % _slash,
        "event_detail", name="event_detail_year"),
    url("^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/"
        "(?P<slug>.*)/event.ics$", "icalendar_event", name="icalendar_event_day"),
    url("^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>.*)/event.ics$",
        "icalendar_event", name="icalendar_event_month"),
    url("^(?P<year>\d{4})/(?P<slug>.*)/event.ics$",
        "icalendar_event", name="icalendar_event_year"),
    url("^(?P<slug>.*)/event.ics$", "icalendar_event", name="icalendar_event"),
    url("^calendar.ics$", "icalendar", name="icalendar"),
    url("^(?P<slug>.*)%s$" % _slash, "event_detail",
        name="event_detail"),
    url("^$", "event_list", name="event_list"),
)
