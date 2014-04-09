from __future__ import unicode_literals
from datetime import datetime

from django import template
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.utils import timezone as tz
from django.utils.http import urlquote as quote

from mezzanine_agenda.models import Event, EventLocation
from mezzanine.conf import settings
from mezzanine.core.managers import SearchableQuerySet
from mezzanine.generic.models import Keyword
from mezzanine.pages.models import Page
from mezzanine.template import Library
from mezzanine.utils.models import get_user_model
from mezzanine.utils.sites import current_site_id

import pytz

from time import strptime

User = get_user_model()

register = Library()


@register.as_tag
def event_months(*args):
    """
    Put a list of dates for events into the template context.
    """
    dates = Event.objects.published().values_list("start", flat=True)
    date_dicts = [{"date": datetime(d.year, d.month, 1)} for d in dates]
    month_dicts = []
    for date_dict in date_dicts:
        if date_dict not in month_dicts:
            month_dicts.append(date_dict)
    for i, date_dict in enumerate(month_dicts):
        month_dicts[i]["event_count"] = date_dicts.count(date_dict)
    return month_dicts


@register.as_tag
def event_locations(*args):
    """
    Put a list of locations for events into the template context.
    """
    events = Event.objects.published()
    locations = EventLocation.objects.filter(event__in=events)
    return list(locations.annotate(event_count=Count("event")))


@register.as_tag
def event_authors(*args):
    """
    Put a list of authors (users) for events into the template context.
    """
    events = Event.objects.published()
    authors = User.objects.filter(events__in=events)
    return list(authors.annotate(event_count=Count("events")))


@register.as_tag
def recent_events(limit=5, tag=None, username=None, location=None):
    """
    Put a list of recent events into the template
    context. A tag title or slug, location title or slug or author's
    username can also be specified to filter the recent events returned.

    Usage::

        {% recent_events 5 as recent_events %}
        {% recent_events limit=5 tag="django" as recent_events %}
        {% recent_events limit=5 location="home" as recent_events %}
        {% recent_events 5 username=admin as recent_pevents %}

    """
    events = Event.objects.published().select_related("user")
    events = events.filter(Q(start__lt=datetime.now()) | Q(end__lt=datetime.now()))
    title_or_slug = lambda s: Q(title=s) | Q(slug=s)
    if tag is not None:
        try:
            tag = Keyword.objects.get(title_or_slug(tag))
            events = events.filter(keywords__keyword=tag)
        except Keyword.DoesNotExist:
            return []
    if location is not None:
        try:
            location = EventLocation.objects.get(title_or_slug(location))
            events = events.filter(location=location)
        except EventLocation.DoesNotExist:
            return []
    if username is not None:
        try:
            author = User.objects.get(username=username)
            events = events.filter(user=author)
        except User.DoesNotExist:
            return []
    return list(events[:limit])


@register.as_tag
def upcoming_events(limit=5, tag=None, username=None, location=None):
    """
    Put a list of upcoming events into the template
    context. A tag title or slug, location title or slug or author's
    username can also be specified to filter the recent events returned.

    Usage::

        {% upcoming_events 5 as upcoming_events %}
        {% upcoming limit=5 tag="django" as upcoming_events %}
        {% upcoming_events limit=5 location="home" as upcoming_events %}
        {% upcoming_events 5 username=admin as upcoming_events %}

    """
    events = Event.objects.published().select_related("user")
    events = events.filter(Q(start__gt=datetime.now()) | Q(end__gt=datetime.now()))
    title_or_slug = lambda s: Q(title=s) | Q(slug=s)
    if tag is not None:
        try:
            tag = Keyword.objects.get(title_or_slug(tag))
            events = events.filter(keywords__keyword=tag)
        except Keyword.DoesNotExist:
            return []
    if location is not None:
        try:
            location = EventLocation.objects.get(title_or_slug(location))
            events = events.filter(location=location)
        except EventLocation.DoesNotExist:
            return []
    if username is not None:
        try:
            author = User.objects.get(username=username)
            events = events.filter(user=author)
        except User.DoesNotExist:
            return []
    return list(events[:limit])


def _get_utc(datetime):
    """
    Convert datetime object to be timezone aware and in UTC.
    """
    if settings.EVENT_TIME_ZONE != "":
        app_tz = pytz.timezone(settings.EVENT_TIME_ZONE)
    else:
        app_tz = tz.get_default_timezone()

    # make the datetime aware
    if tz.is_naive(datetime):
        datetime = tz.make_aware(datetime, app_tz)

    # now, make it UTC
    datetime = tz.make_naive(datetime, tz.utc)

    return datetime


@register.filter(is_safe=True)
def google_calendar_url(event):
    """
    Generates a link to add the event to your google calendar.
    """
    if not isinstance(event, Event):
        return ''
    title = quote(event.title)
    start_date = _get_utc(event.start).strftime("%Y%m%dT%H%M%SZ")
    if event.end:
        end_date = _get_utc(event.end).strftime("%Y%m%dT%H%M%SZ")
    else:
        end_date = start_date
    url = Site.objects.get(id=current_site_id()).domain + event.get_absolute_url()
    if event.location:
        location = quote(event.location.mappable_location)
    else:
        location = None
    return "http://www.google.com/calendar/event?action=TEMPLATE&text={title}&dates={start_date}/{end_date}&sprop=website:{url}&location={location}&trp=true".format(**locals())


@register.filter(is_safe=True)
def google_nav_url(event):
    """
    Generates a link to get directions to an event with google maps.
    """
    if not isinstance(event, Event):
        return ''
    location = quote(event.location.mappable_location)
    return "https://{}/maps?daddr={}".format(settings.EVENT_GOOGLE_MAPS_DOMAIN.decode('utf-8'), location)


@register.simple_tag
def google_static_map(event, width, height, zoom):
    """
    Generates a static google map for the event location.
    """
    marker = quote('{:.6},{:.6}'.format(event.location.lat, event.location.lon))
    if settings.EVENT_HIDPI_STATIC_MAPS:
        scale = 2
    else:
        scale = 1
    return "<img src='http://maps.googleapis.com/maps/api/staticmap?size={width}x{height}&scale={scale}&format=png&markers={marker}&sensor=false&zoom={zoom}' width='{width}' height='{height}' />".format(**locals())


@register.simple_tag(takes_context=True)
def icalendar_url(context):
    """
    Generates the link to the icalendar view for the current page.
    """
    if context.get("event"):
        return "%sevent.ics" % context["event"].get_absolute_url()
    else:
        if context.get("tag"):
            return reverse("icalendar_tag", args=(context["tag"],))
        elif context.get("year") and context.get("month"):
            return reverse("icalendar_month", args=(context["year"], strptime(context["month"], '%B').tm_mon))
        elif context.get("year"):
            return reverse("icalendar_year", args=(context["year"],))
        elif context.get("location"):
            return reverse("icalendar_location", args=(context["location"].slug,))
        elif context.get("author"):
            return reverse("icalendar_author", args=(context["author"],))
        else:
            return reverse("icalendar")
