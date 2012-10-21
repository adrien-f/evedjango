from django.db import models
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from datetime import datetime, timedelta

from django.dispatch import receiver

from managers import APIKeyInfoManager

import eveapi

REVERSE_KEY_MAP = { 'Account': 'AC', 'Character': 'CH', 'Corporation': 'CO', 'Unknown': 'UN' }

def get_sentinel_key():
    return APIKey.objects.get_or_create(id='0')[0]

class APIKey(models.Model):
    id = models.IntegerField(primary_key=True, editable=True)
    vcode = models.CharField(max_length=64, editable=True)
    owner = models.ForeignKey(User, related_name='user_api_keys', null=True, blank=False)

    # This is solely for access restrictions that can be removed
    # by setting API_KEY_SITE_LOCK = False;  This defaults to 
    # True to prevent bad behavior on the part of the developer (both of us).
    # Either way, this is included for developers who actively use the sites
    # framework.  If you do not wish to use it, set "EVE_DISABLE_SITES" in 
    # in your settings.py
    if getattr(settings, "EVE_DISABLE_SITES", False):
        site = models.ForeignKey(Site, related_name='site_api_keys')

    def get_api_object(self):
        api = eveapi.EVEAPIConnection()
        try:
            return api.auth(keyID=self.id, vCode=self.vcode)
        except eveapi.ServerError as e:
            # TODO: Handle this
            return None
        except eveapi.AuthenticationError as e: 
            # No such object any more
            self.delete()
            return None

    def get_key_info(self):
        return APIKeyInfo.objects.get_or_create(apikey=self)[0]

class APIKeyInfo(models.Model):
    UNKNOWN = 'UN'
    ACCOUNT = 'AC'
    CHARACTER = 'CH'
    CORPORATION = 'CO'
    KEY_TYPE_CHOICES = (
            (UNKNOWN, 'Unknown'),
            (ACCOUNT, 'Account'),
            (CHARACTER, 'Character'),
            (CORPORATION, 'Corporation'),
    )
    apikey = models.ForeignKey(APIKey,
                                  primary_key=True,
                                  related_name='info',
                                  unique=True,
                                  db_index=True,
                                  editable=False)
    key_type = models.CharField(
                                max_length=2,
                                choices=KEY_TYPE_CHOICES,
                                default="UK",
                                db_index=True, editable=False
                                )
    access_mask = models.IntegerField(editable=False)
    cached_until = models.DateTimeField(null=True, blank=False, editable=False)
    expires_on = models.DateTimeField(null=True, blank=False, editable=False)

    objects = APIKeyInfoManager()

    def update_with_auth(self, auth):

        key_info = auth.account.APIKeyInfo()
        self.access_mask = key_info.key.accessMask
        typeindx = key_info.key.type
        if typeindx not in REVERSE_KEY_MAP.keys():
            typecode = 'UN'
        else:
            typecode = REVERSE_KEY_MAP[typeindx]

        self.key_type = typecode

        default_cache = datetime.now() + timedelta(1/12)

        self.cached_until = getattr(key_info.key, 'cachedUntil', default_cache)

        if key_info.key.expires is u'':
            self.expires_on = None
        else:
            self.expires_on = key_info.key.expires

    def has_mask(self, mask):
        return self.access_mask & mask == mask

    def is_corporation(self):
        return self.key_type == self.CORPORATION

    def is_character(self):
        return self.key_type == self.CHARACTER

    def is_account(self):
        return self.key_type == self.ACCOUNT

@receiver(pre_save, sender=APIKeyInfo)
def api_key_info_save_handler(sender, instance, **kwargs):
    # Already saved once before; to prevent spamming EVE API beyond cachedUntil
    auth = instance.apikey.get_api_object()
    key_info = auth.account.APIKeyInfo()

    current_time = getattr(key_info.key, 'currentTime', datetime.now())

    if not instance.pk or (instance.cached_until < current_time):
        instance.update_with_auth(auth)


@receiver(post_save, sender=APIKey)
def api_key_save_handler(sender, instance, **kwargs):
    auth = instance.get_api_object()
    key_info = auth.account.APIKeyInfo()
    default_cache = datetime.now() + timedelta(1)

    pass_args = {
            'apikey': instance,
            'key_type': getattr(REVERSE_KEY_MAP, key_info.key.type, 'UN'),
            'access_mask': getattr(key_info.key, 'accessMask'),
            'cached_until': getattr(key_info.key, 'cachedUntil', default_cache),
            }
    expires_on = getattr(key_info.key, 'expires', None)
    if expires_on:
        if expires_on is not u'':
            pass_args['expires_on'] = expires_on
    api_key_info, created = APIKeyInfo.objects.get_or_create(
                                                **pass_args
                                            )
    if not created:
        raise AttributeError("Welp.")

