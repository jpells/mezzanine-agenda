from __future__ import unicode_literals
from future.builtins import str

from django.db import models
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from geopy.geocoders import GoogleV3 as GoogleMaps
from geopy.geocoders.googlev3 import GQueryError

from icalendar import Event as IEvent

from mezzanine.conf import settings
from mezzanine.core.fields import FileField
from mezzanine.core.models import Displayable, Ownable, RichText, Slugged
from mezzanine.generic.fields import CommentsField, RatingField
from mezzanine.utils.models import AdminThumbMixin, upload_to
from mezzanine.utils.sites import current_site_id


class Event(Displayable, Ownable, RichText, AdminThumbMixin):
    """
    A event.
    """

    start = models.DateTimeField(_("Start"))
    end = models.DateTimeField(_("End"), blank=True, null=True)
    location = models.ForeignKey("EventLocation", blank=True, null=True)
    facebook_event = models.BigIntegerField(_('Facebook'), blank=True, null=True) #
    allow_comments = models.BooleanField(verbose_name=_("Allow comments"),
                                         default=True)
    comments = CommentsField(verbose_name=_("Comments"))
    rating = RatingField(verbose_name=_("Rating"))
    featured_image = FileField(verbose_name=_("Featured Image"),
        upload_to=upload_to("mezzanine_agenda.Event.featured_image", "event"),
        format="Image", max_length=255, null=True, blank=True)

    admin_thumb_field = "featured_image"

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        ordering = ("-start",)

    def clean(self):
        """
        Validate end date is after the start date.
        """
        super(Event, self).clean()

        if self.end and self.start > self.end:
            raise ValidationError("Start must be sooner than end.")

    def get_absolute_url(self):
        """
        URLs for events can either be just their slug, or prefixed
        with a portion of the post's publish date, controlled by the
        setting ``EVENT_URLS_DATE_FORMAT``, which can contain the value
        ``year``, ``month``, or ``day``. Each of these maps to the name
        of the corresponding urlpattern, and if defined, we loop through
        each of these and build up the kwargs for the correct urlpattern.
        The order which we loop through them is important, since the
        order goes from least granualr (just year) to most granular
        (year/month/day).
        """
        url_name = "event_detail"
        kwargs = {"slug": self.slug}
        date_parts = ("year", "month", "day")
        if settings.EVENT_URLS_DATE_FORMAT in date_parts:
            url_name = "event_detail_%s" % settings.EVENT_URLS_DATE_FORMAT
            for date_part in date_parts:
                date_value = str(getattr(self.publish_date, date_part))
                if len(date_value) == 1:
                    date_value = "0%s" % date_value
                kwargs[date_part] = date_value
                if date_part == settings.EVENT_URLS_DATE_FORMAT:
                    break
        return reverse(url_name, kwargs=kwargs)

    def get_icalendar_event(self):
        """
        Builds an icalendar.event object from event data.
        """
        icalendar_event = IEvent()
        icalendar_event.add('summary'.encode("utf-8"), self.title)
        icalendar_event.add('url', 'http://{domain}{url}'.format(
            domain=Site.objects.get(id=current_site_id()).domain,
            url=self.get_absolute_url(),
        ))
        if self.location:
            icalendar_event.add('location'.encode("utf-8"), self.location.address)
        icalendar_event.add('dtstamp', self.start)
        icalendar_event.add('dtstart', self.start)
        if self.end:
            icalendar_event.add('dtend', self.end)
        icalendar_event['uid'.encode("utf-8")] = "event-{id}@{domain}".format(
            id=self.id,
            domain=Site.objects.get(id=current_site_id()).domain,
        ).encode("utf-8")
        return icalendar_event


class EventLocation(Slugged):
    """
    A Event Location.
    """

    address = models.TextField()
    mappable_location = models.CharField(max_length=128, blank=True, help_text="This address will be used to calculate latitude and longitude. Leave blank and set Latitude and Longitude to specify the location yourself, or leave all three blank to auto-fill from the Location field.")
    lat = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, verbose_name="Latitude", help_text="Calculated automatically if mappable location is set.")
    lon = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, verbose_name="Longitude", help_text="Calculated automatically if mappable location is set.")

    class Meta:
        verbose_name = _("Event Location")
        verbose_name_plural = _("Event Locations")
        ordering = ("title",)

    def clean(self):
        """
        Validate set/validate mappable_location, longitude and latitude.
        """
        super(EventLocation, self).clean()

        if self.lat and not self.lon:
            raise ValidationError("Longitude required if specifying latitude.")

        if self.lon and not self.lat:
            raise ValidationError("Latitude required if specifying longitude.")

        if not (self.lat and self.lon) and not self.mappable_location:
            self.mappable_location = self.address.replace("\n",", ")

        if self.mappable_location and not (self.lat and self.lon): #location should always override lat/long if set
            g = GoogleMaps(domain=settings.EVENT_GOOGLE_MAPS_DOMAIN)
            try:
                mappable_location, (lat, lon) = g.geocode(self.mappable_location.encode('utf-8'))
            except GQueryError as e:
                raise ValidationError("The mappable location you specified could not be found on {service}: \"{error}\" Try changing the mappable location, removing any business names, or leaving mappable location blank and using coordinates from getlatlon.com.".format(service="Google Maps", error=e.message))
            except ValueError as e:
                raise ValidationError("The mappable location you specified could not be found on {service}: \"{error}\" Try changing the mappable location, removing any business names, or leaving mappable location blank and using coordinates from getlatlon.com.".format(service="Google Maps", error=e.message))
            self.mappable_location = mappable_location
            self.lat = lat
            self.lon = lon

    @models.permalink
    def get_absolute_url(self):
        return ("event_list_location", (), {"location": self.slug})
