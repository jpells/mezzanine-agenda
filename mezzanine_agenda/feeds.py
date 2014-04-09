from __future__ import unicode_literals

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.utils.html import strip_tags

from mezzanine.core.templatetags.mezzanine_tags import richtext_filters
from mezzanine_agenda.models import Event, EventLocation
from mezzanine.generic.models import Keyword
from mezzanine.pages.models import Page
from mezzanine.conf import settings
from mezzanine.utils.models import get_user_model


User = get_user_model()


class EventsRSS(Feed):
    """
    RSS feed for all events.
    """

    def __init__(self, *args, **kwargs):
        """
        Use the title and description of the Events page for the feed's
        title and description. If the events page has somehow been
        removed, fall back to the ``SITE_TITLE`` and ``SITE_TAGLINE``
        settings.
        """
        self.tag = kwargs.pop("tag", None)
        self.location = kwargs.pop("location", None)
        self.username = kwargs.pop("username", None)
        super(EventsRSS, self).__init__(*args, **kwargs)
        self._public = True
        try:
            page = Page.objects.published().get(slug=settings.EVENT_SLUG)
        except Page.DoesNotExist:
            page = None
        else:
            self._public = not page.login_required
        if self._public:
            settings.use_editable()
            if page is not None:
                self._title = "%s | %s" % (page.title, settings.SITE_TITLE)
                self._description = strip_tags(page.description)
            else:
                self._title = settings.SITE_TITLE
                self._description = settings.SITE_TAGLINE

    def title(self):
        return self._title

    def description(self):
        return self._description

    def link(self):
        return reverse("event_list")

    def items(self):
        if not self._public:
            return []
        events = Event.objects.published().select_related("user")
        if self.tag:
            tag = get_object_or_404(Keyword, slug=self.tag)
            events = events.filter(keywords__keyword=tag)
        if self.location:
            location = get_object_or_404(EventLocation, slug=self.location)
            events = events.filter(location=location)
        if self.username:
            author = get_object_or_404(User, username=self.username)
            events = events.filter(user=author)
        limit = settings.EVENT_RSS_LIMIT
        if limit is not None:
            events = events[:settings.EVENT_RSS_LIMIT]
        return events

    def item_description(self, item):
        return richtext_filters(item.content)

    def locations(self):
        if not self._public:
            return []
        return EventLocations.objects.all()

    def item_author_name(self, item):
        return item.user.get_full_name() or item.user.username

    def item_author_link(self, item):
        username = item.user.username
        return reverse("event_list_author", kwargs={"username": username})

    def item_pubdate(self, item):
        return item.publish_date

    def item_location(self, item):
        return item.location


class EventsAtom(EventsRSS):
    """
    Atom feed for all events.
    """

    feed_type = Atom1Feed

    def subtitle(self):
        return self.description()
