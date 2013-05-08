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
    if not getattr(settings, "EVE_DISABLE_SITES", False):
        site = models.ForeignKey(Site, related_name='site_api_keys', default=settings.SITE_ID)

    class Meta:
        if not getattr(settings, "EVE_DISABLE_SITES", False):
            unique_together = ('id', 'site')
        else:
            pass

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
        return APIKeyInfo.objects.get_or_create(api_key=self)[0]

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
    api_key = models.OneToOneField(
                                  APIKey,
                                  related_name='info',
                                  unique=True,
                                  db_index=True,
                                  editable=False
                                  )
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

        self.cached_until = getattr(key_info, 'cachedUntil', default_cache)

        if key_info.key.expires is u'':
            self.expires_on = None
        else:
            expires_on = datetime.fromtimestamp(key_info.key.expires)
            self.expires_on = expires_on

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
    auth = instance.api_key.get_api_object()
    key_info = auth.account.APIKeyInfo()

    current_time = getattr(key_info.key, 'currentTime', datetime.now())

    if not instance.pk or (instance.cached_until < current_time):
        instance.update_with_auth(auth)


@receiver(post_save, sender=APIKey)
def api_key_save_handler(sender, instance, **kwargs):
    auth = instance.get_api_object()
    key_info = auth.account.APIKeyInfo()
    default_cache = datetime.now() + timedelta(1)
    key_type = REVERSE_KEY_MAP.get(key_info.key.type, 'UN')

    if key_type in ['CH', 'AC']:
        [Character.create_from_api_set(row).save() for row in key_info.key.characters]

    pass_args = {
            'api_key': instance,
            'key_type': key_type,
            'access_mask': getattr(key_info.key, 'accessMask'),
            'cached_until': getattr(key_info.key, 'cachedUntil', default_cache),
            }
    expires_on = getattr(key_info.key, 'expires', None)
    if expires_on is not None:
        if expires_on is not u'':
            pass_args['expires_on'] = datetime.fromtimestamp(expires_on)
    api_key_info, created = APIKeyInfo.objects.get_or_create(
                                                **pass_args
                                            )
    if not created:
        raise AttributeError("Welp.")

class EveEntity(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    api_keys = models.ManyToManyField(APIKeyInfo, related_name='%(app_label)s_%(class)s_entities')

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
                    self.alliance.save()
            if corp_sheet.factionID != 0:
                self.faction = ChrFaction.objects.get(pk=corp_sheet.factionID)
            self.save()

class Character(EveEntity):
    corporation = models.ForeignKey(Corporation)
    alliance = models.ForeignKey(Alliance, blank=False, null=True)
    faction = models.ForeignKey(ChrFaction, blank=False, null=True)

    @classmethod
    def create_from_api_set(cls, api_set, api_key=None):

        character = Character(id=api_set.characterID)

        try:
            character.faction = ChrFaction.objects.get(
                    pk=getattr(api_set, 'factionID', None)
                    )
        except ChrFaction.DoesNotExist:
            character.faction = None

        try:
            character.alliance = Alliance.objects.get(
                    pk=getattr(api_set, 'allianceID', 0)
                    )
        except Alliance.DoesNotExist:
            if getattr(api_set, 'allianceID', 0)  == 0:
                character.alliance = None
            else:
                character.alliance = Alliance(
                        id=api_set.allianceID,
                        name=api_set.allianceName,
                        faction=character.faction,
                        ).save()
        try:
            character.corporation = Corporation.objects.get(
                    pk=api_set.corporationID
                    )
        except Corporation.DoesNotExist:
            corp = Corporation(
                    id=api_set.corporationID,
                    name=api_set.corporationName,
                    alliance=character.alliance,
                    faction=character.faction
                    )
            corp.save()
            character.corporation = corp

        if api_key is not None:
            character.api_keys.add(api_key)

        character.save()
        return character

class Victim(models.Model):
    character = models.ForeignKey(Character, related_name="deaths")
    damage_taken = models.IntegerField()
    ship_type = models.ForeignKey(InvType)

    @classmethod
    def create_from_victim_set(cls, victim_set, api_key=None):

        try:
            character = Character.objects.get(pk=victim_set.characterID)
        except Character.DoesNotExist:
            character = Character.create_from_api_set(victim_set, api_key).save()

        victim = cls(
                character=character,
                damage_taken=victim_set.damageTaken,
                ship_type=InvType(pk=victim_set.shipTypeID))

        victim.save()

        return victim

class Attacker(models.Model):
    character = models.ForeignKey(Character, related_name="kills")
    sec_status = models.FloatField()
    damage_done = models.IntegerField()
    final_blow = models.BooleanField()
    weapon_type = models.ForeignKey(InvType, related_name="used_by_attackers")
    ship_type = models.ForeignKey(InvType, related_name="flown_by_attackers")

    @classmethod
    def create_from_attacker_set(cls, att_set, api_key=None):
        try:
            character = Character.objects.get(pk=att_set.characterID)
        except Character.DoesNotExist:
            character = Character.create_from_api_set(att_set, api_key)

        return cls(
                character=character,
                sec_status=float(att_set.securityStatus),
                damage_done=att_set.damageDone,
                final_blow=bool(att_set.finalBlow),
                weapon_type=InvType.objects.get(pk=att_set.weaponTypeID),
                ship_type=InvType.objects.get(pk=att_set.shipTypeID),
                ).save()

class CharacterProfile(models.Model):
    character = models.OneToOneField(Character, related_name="profile", unique=True)
    api_key = models.ForeignKey(APIKey, related_name="character_profile")

class ItemDrop(models.Model):
    kill_report = models.ForeignKey(InvType, related_name="item_drops")
    item_type = models.ForeignKey(InvType)
    location_flag = models.IntegerField(default=0)
    container = models.ForeignKey("self", related_name="contains", blank=False, null=True)
    qty_dropped = models.IntegerField(default=0)
    qty_destroyed = models.IntegerField(default=0)
    singleton = models.IntegerField(default=0)

    @classmethod
    def create_from_item_row(cls, item_row, kill_report, container=None):
        item_drop = cls(
                    kill_report=kill_report,
                    item_type=InvType.objects.get(pk=item_row.typeID),
                    location_flag=getattr(item_row, 'flag', 0),
                    container=container,
                    qty_dropped=getattr(item_row, 'qtyDropped', 0),
                    qty_destroyed=getattr(item_row, 'qtyDestroyed', 0),
                    singleton=getattr(item_row, 'singleton', 0),
                )
        item_drop.save()

        if hasattr(item_row, 'items'):
            item_drop=[item_drop]
            for item in item_row.items:
                item_drop.append(cls.create_from_item_row(item, container=item_drop))

        return item_drop

class KillReport(EveEntity):
    solar_system = models.ForeignKey(MapSolarSystem, related_name='system_kills')
    kill_time = models.DateTimeField(blank=False, null=False)
    victim = models.ForeignKey(Victim, related_name='victim_reports')
    attackers = models.ManyToManyField(Attacker, related_name='confirmed_kills')

    objects = KillReportManager()

    class Meta:
        unique_together = ('id', 'victim')
    
    @classmethod
    def create_from_kill_row(cls, kill_row, api_key=None):
        kill_id = kill_row.killID
        try:
            kill_report = cls.objects.get(pk=kill_id)
        except cls.DoesNotExist:
            pass
        else:
            return kill_report, kill_report.drops
        kill_time = kill_row.killTime
        kill_system = kill_row.solarSystemID
        victim_set = kill_row.victim
        attackers_rowset = kill_row.attackers
        items_rowset = kill_row.items

        # defaults
        alliance = None
        faction = None

        victim = Victim.create_from_victim_set(victim_set, api_key).save()
        attackers = [Attacker.create_from_attacker_set(att_set, api_key).save() for att_set in attackers_rowset]
        solsystem = MapSolarSystem(pk=kill_system)

        kill_report = cls(
                id=kill_id,
                name='Kill Report',
                api_keys=[api_key,],
                solar_system=solsystem,
                kill_time=kill_time,
                victim=victim,
                attackers=attackers,
                )

        kill_report.save()

        drops = []

        for item_set in items_rowset:
            drop = ItemDrop.create_from_item_row(item_set, kill_report)
            try:
                tmp_drops = [item_drop for item_drop in drop]
            except TypeError:
                drops.append(drop)
            else:
                drops += drop

        return kill_report, drops

