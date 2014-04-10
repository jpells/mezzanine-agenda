from __future__ import unicode_literals
from future.builtins import str
from future.builtins import int
from calendar import month_name

from datetime import datetime

from django.contrib.sites.models import Site
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404

from icalendar import Calendar

from mezzanine_agenda import __version__
from mezzanine_agenda.models import Event, EventLocation
from mezzanine_agenda.feeds import EventsRSS, EventsAtom
from mezzanine.conf import settings
from mezzanine.generic.models import Keyword
from mezzanine.pages.models import Page
from mezzanine.utils.views import render, paginate
from mezzanine.utils.models import get_user_model
from mezzanine.utils.sites import current_site_id

User = get_user_model()


def event_list(request, tag=None, year=None, month=None, username=None,
                   location=None, template="agenda/event_list.html"):
    """
    Display a list of events that are filtered by tag, year, month,
    author or location. Custom templates are checked for using the name
    ``agenda/event_list_XXX.html`` where ``XXX`` is either the
    location slug or author's username if given.
    """
    settings.use_editable()
    templates = []
    events = Event.objects.published(for_user=request.user)
    if tag is not None:
        tag = get_object_or_404(Keyword, slug=tag)
        events = events.filter(keywords__keyword=tag)
    if year is not None:
        events = events.filter(start__year=year)
        if month is not None:
            events = events.filter(start__month=month)
            try:
                month = month_name[int(month)]
            except IndexError:
                raise Http404()
    if location is not None:
        location = get_object_or_404(EventLocation, slug=location)
        events = events.filter(location=location)
        templates.append(u"agenda/event_list_%s.html" %
                          str(location.slug))
    author = None
    if username is not None:
        author = get_object_or_404(User, username=username)
        events = events.filter(user=author)
        templates.append(u"agenda/event_list_%s.html" % username)
    if not tag and not year and not location and not username:
        #Get upcoming events/ongoing events
        events = events.filter(Q(start__gt=datetime.now()) | Q(end__gt=datetime.now())).order_by("start")

    prefetch = ("keywords__keyword",)
    events = events.select_related("user").prefetch_related(*prefetch)
    events = paginate(events, request.GET.get("page", 1),
                          settings.EVENT_PER_PAGE,
                          settings.MAX_PAGING_LINKS)
    context = {"events": events, "year": year, "month": month,
               "tag": tag, "location": location, "author": author}
    templates.append(template)
    return render(request, templates, context)


def event_detail(request, slug, year=None, month=None, day=None,
                     template="agenda/event_detail.html"):
    """. Custom templates are checked for using the name
    ``agenda/event_detail_XXX.html`` where ``XXX`` is the agenda
    events's slug.
    """
    events = Event.objects.published(
                                     for_user=request.user).select_related()
    event = get_object_or_404(events, slug=slug)
    context = {"event": event, "editable_obj": event}
    templates = [u"agenda/event_detail_%s.html" % str(slug), template]
    return render(request, templates, context)


def event_feed(request, format, **kwargs):
    """
    Events feeds - maps format to the correct feed view.
    """
    try:
        return {"rss": EventsRSS, "atom": EventsAtom}[format](**kwargs)(request)
    except KeyError:
        raise Http404()


def _make_icalendar():
    """
    Create an icalendar object.
    """
    icalendar = Calendar()
    icalendar.add('prodid',
        '-//mezzanine-agenda//NONSGML V{}//EN'.format(__version__))
    icalendar.add('version', '2.0') # version of the format, not the product!
    return icalendar


def icalendar_event(request, slug, year=None, month=None, day=None):
    """
    Returns the icalendar for a specific event.
    """
    events = Event.objects.published(
                                     for_user=request.user).select_related()
    event = get_object_or_404(events, slug=slug)

    icalendar = _make_icalendar()
    icalendar_event = event.get_icalendar_event()
    icalendar.add_component(icalendar_event)

    return HttpResponse(icalendar.to_ical(), content_type="text/calendar")


def icalendar(request, tag=None, year=None, month=None, username=None,
                   location=None):
    """
    Returns the icalendar for a group of events that are filtered by tag,
    year, month, author or location.
    """
    settings.use_editable()
    events = Event.objects.published(for_user=request.user)
    if tag is not None:
        tag = get_object_or_404(Keyword, slug=tag)
        events = events.filter(keywords__keyword=tag)
    if year is not None:
        events = events.filter(start__year=year)
        if month is not None:
            events = events.filter(start__month=month)
            try:
                month = month_name[int(month)]
            except IndexError:
                raise Http404()
    if location is not None:
        location = get_object_or_404(EventLocation, slug=location)
        events = events.filter(location=location)
    author = None
    if username is not None:
        author = get_object_or_404(User, username=username)
        events = events.filter(user=author)
    if not tag and not year and not location and not username:
        #Get upcoming events/ongoing events
        events = events.filter(Q(start__gt=datetime.now()) | Q(end__gt=datetime.now())).order_by("start")

    prefetch = ("keywords__keyword",)
    events = events.select_related("user").prefetch_related(*prefetch)

    icalendar = _make_icalendar()
    for event in events:
        icalendar_event = event.get_icalendar_event()
        icalendar.add_component(icalendar_event)

    return HttpResponse(icalendar.to_ical(), content_type="text/calendar")
