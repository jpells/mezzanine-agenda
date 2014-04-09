from __future__ import unicode_literals

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.utils.unittest import skipUnless

from mezzanine_agenda.models import Event, EventLocation
from mezzanine.conf import settings

from mezzanine.core.models import CONTENT_STATUS_DRAFT, CONTENT_STATUS_PUBLISHED
from mezzanine.pages.models import RichTextPage
from mezzanine.utils.tests import TestCase

from datetime import datetime


class EventTests(TestCase):

    def setUp(self):
        super(EventTests, self).setUp()
        self.eventlocation = EventLocation.objects.create(
            address='1 Susan St\nHindmarsh\nSouth Australia',
        )
        self.eventlocation.save()
        self.unicode_eventlocation = EventLocation.objects.create(
            address='\u30b5\u30f3\u30b7\u30e3\u30a4\u30f360',
        )
        self.unicode_eventlocation.save()
        self.event = Event.objects.create(
            slug='events/blah',
            title='THIS IS AN EVENT THAT IS PUBLISHED',
            start=datetime.now(),
            end=datetime.now()+timedelta(hours=4),
            location=self.eventlocation,
            status=CONTENT_STATUS_PUBLISHED,
            user=self._user,
        )
        self.event.save()
        self.draft_event = Event.objects.create(
            slug='events/draft',
            title='THIS IS AN EVENT THAT IS A DRAFT',
            start=datetime.now(),
            end=datetime.now()+timedelta(hours=4),
            location=self.eventlocation,
            status=CONTENT_STATUS_DRAFT,
            user=self._user,
        )
        self.draft_event.save()
        self.unicode_event = Event.objects.create(
            slug='cont/\u30b5\u30f3\u30b7\u30e3\u30a4\u30f360',
            title='\xe9\x9d\x9eASCII\xe3\x82\xbf\xe3\x82\xa4\xe3\x83\x88\xe3\x83\xab',
            start=datetime.now(),
            end=datetime.now()+timedelta(hours=4),
            location=self.unicode_eventlocation,
            status=CONTENT_STATUS_PUBLISHED,
            user=self._user,
        )
        self.unicode_event.save()
        self.events = (self.event, self.unicode_event)
        self.event_page = RichTextPage.objects.create(title="events", slug=settings.EVENT_SLUG)


    def test_event_views(self):
        """
        Basic status code test for agenda views.
        """
        response = self.client.get(reverse("event_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title)
        self.assertNotContains(response, self.draft_event.title)
        response = self.client.get(reverse("event_feed", args=("rss",)))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("event_feed", args=("atom",)))
        self.assertEqual(response.status_code, 200)
        event = Event.objects.create(title="Event", start=datetime.now(), user=self._user,
                                            status=CONTENT_STATUS_PUBLISHED)
        response = self.client.get(event.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    @skipUnless("mezzanine.accounts" in settings.INSTALLED_APPS and
                "mezzanine.pages" in settings.INSTALLED_APPS,
                "accounts and pages apps required")
    def test_login_protected_event(self):
        """
        Test the events is login protected if its page has login_required
        set to True.
        """
        self.event_page.login_required=True
        self.event_page.save()
        response = self.client.get(reverse("event_list"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.redirect_chain) > 0)
        redirect_path = urlparse(response.redirect_chain[0][0]).path
        self.assertEqual(redirect_path, settings.LOGIN_URL)
        self.event_page.login_required=False
        self.event_page.save()

    def test_clean(self):
        """
        Test the events geocoding functionality.
        """
        self.eventlocation.clean()
        self.assertAlmostEqual(self.eventlocation.lat, -34.907924, places=5)
        self.assertAlmostEqual(self.eventlocation.lon, 138.567624, places=5)
        self.assertEqual(self.eventlocation.mappable_location, '1 Susan Street, Hindmarsh SA 5007, Australia')
        self.unicode_eventlocation.clean()
        self.assertAlmostEqual(self.unicode_eventlocation.lat, 35.729534, places=5)
        self.assertAlmostEqual(self.unicode_eventlocation.lon, 139.718055, places=5)

    def test_icalendars(self):
        """
        Test the icalendar views.
        """
        for event in self.events:
            response = self.client.get(reverse("icalendar_event", args=(event.slug,)))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'text/calendar')
        response = self.client.get(reverse("icalendar"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/calendar')
