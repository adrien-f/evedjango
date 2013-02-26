from django import template
from corpmgr.models import CorporationProfile

register = template.Library()

def is_director(user):
    if user.is_authenticated():
        for profile in CorporationProfile.objects.all():
            if profile.has_director(user):
                return True

    return False

register.filter('is_director', is_director)
