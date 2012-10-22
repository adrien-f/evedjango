from django.db import models
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from datetime import datetime, timedelta

from django.dispatch import receiver

from managers import APIKeyInfoManager, KillReportManager

from eve_db.models import InvType, MapSolarSystem, ChrFaction

import eveapi

REVERSE_KEY_MAP = { 'Account': 'AC', 'Character': 'CH', 'Corporation': 'CO', 'Unknown': 'UN' }

def get_sentinel_key():
    return APIKey.objects.get_or_create(id='0')[0]

class APIKey(models.Model):
    id = models.IntegerField(primary_key=True, editable=True)
    vcode = models.CharField(max_length=64, editable=True)
    owner = models.ForeignKey(User, related_name='user_api_keys', null=True, blank=False)

    # This is solely for access restrictions that can be removed
    # by setting EVE_DISABLE_SITES = False;  This defaults to 
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
                                default="UN",
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
            'key_type': REVERSE_KEY_MAP.get(key_info.key.type, 'UN'),
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

class EveEntity(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)

    class Meta:
        abstract=True

class Alliance(EveEntity):
    faction = models.ForeignKey(ChrFaction, related_name="militia_member_alliances", blank=False, null=True)

class Corporation(EveEntity):
    alliance = models.ForeignKey(Alliance, related_name="member_corps", blank=False, null=True)
    faction = models.ForeignKey(ChrFaction, related_name="militia_member_corps", blank=False, null=True)

    def fetch_and_save(self):
        if self.pk:
            api = eveapi.EVEAPIConnection()
            corp_sheet = api.corp.CorporationSheet(corporationID=self.pk)
            self.name = corp_sheet.corporationName
            if corp_sheet.allianceID != 0:
                self.alliance = Alliance.objects.get_or_create(pk=corp_sheet.allianceID)
                if not self.alliance.name:
                    self.alliance.name = corp_sheet.allianceName
                    if corp_sheet.factionID != 0:
                        self.alliance.faction = ChrFaction.objects.get(pk=corp_sheet.factionID)
                    alliance.save()
            if corp_sheet.factionID != 0:
                self.faction = ChrFaction.objects.get(pk=corp_sheet.factionID)
            self.save()

class Character(EveEntity):
    corporation = models.ForeignKey(Corporation)
    alliance = models.ForeignKey(Alliance, blank=False, null=True)
    faction = models.ForeignKey(ChrFaction, blank=False, null=True)

    class Meta:
        abstract=True

    def fetch_and_save(self):
        if self.pk:
            api = eveapi.EVEAPIConnection()
            char_info = api.char.CharacterInfo(characterID=self.pk)
            self.name = char_info.characterName
            if char_info.factionID != 0:
                self.faction = ChrFaction.objects.get(pk=char_info.factionID)
            if char_info.allianceID != 0:
                self.alliance = Alliance.objects.get_or_create(pk=char_info.allianceID)
                if not self.alliance.name:
                    self.alliance.name = char_info.allianceName
                    if self.faction:
                        self.alliance.faction = self.faction
                    alliance.save()
            self.corporation = Corporation.objects.get_or_create(pk=char_info.corporationID)
            if not self.corporation.name:
                self.corporation.fetch_and_save()
            self.save()

class Victim(Character):
    damage_taken = models.IntegerField()
    ship_type = models.ForeignKey(InvType)

class Attacker(Character):
    sec_status = models.FloatField()
    damage_done = models.IntegerField()
    final_blow = models.BooleanField()
    damage_done = models.IntegerField()
    weapon_type = models.ForeignKey(InvType, related_name="used_by_attackers")
    ship_type = models.ForeignKey(InvType, related_name="flown_by_attackers")

class ItemDrop(models.Model):
    item_type = models.ForeignKey(InvType)
    location_flag = models.IntegerField(default=0)
    container = models.ForeignKey("self", related_name="contains", blank=False, null=True)
    qty_dropped = models.IntegerField(default=0)
    qty_destroyed = models.IntegerField(default=0)
    singleton = models.IntegerField(default=0)

class KillReport(EveEntity):
    solar_system = models.ForeignKey(MapSolarSystem, related_name='system_kills')
    kill_time = models.DateTimeField(blank=False, null=False)
    victim = models.ForeignKey(Victim, related_name='victim_reports')
    attackers = models.ManyToManyField(Attacker, related_name='confirmed_kills')
    items = models.ManyToManyField(ItemDrop)

    objects = KillReportManager()

    class Meta:
        unique_together = ('id', 'victim')

