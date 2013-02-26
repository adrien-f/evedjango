from django.db import models
from eveauth.models import Corporation, Character, Alliance, APIKey
from account.models import Account
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import managers

from django.db.models.signals import post_save
from django.dispatch import receiver

class CorporationProfile(models.Model):
    corporation = models.OneToOneField(Corporation, related_name='mgmt_profile')
    manager = models.ForeignKey(User, related_name='corps_managed', unique=True)
    director_group = models.OneToOneField(Group, related_name='directors_of')
    api_mask = models.IntegerField()
    reddit_required = models.BooleanField(default=False)
    alliance_profile = models.ForeignKey('AllianceProfile', related_name='member_corp_profiles', blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ( 'corporation', 'alliance_profile' )

    def has_director(self, user):
        try:
            return self.director_group in user.groups.all()
        except:
            # Safer this way.
            return False

    def get_directors(self):
        return self.director_group.users.all()

    def is_alliance(self):
        if hasattr(self, 'executor_of'):
            if self.executor_of.exists():
                return True

        return False

    def get_applications(self, status=None):
        apps = []
        if hasattr(self, 'member_applications'):
            if status is not None:
                try:
                    apps = CorporationApplication.objects.filter(
                            corporation_profile = self, 
                            status__in = status,
                            )
                except:
                    apps = CorporationApplication.objects.filter(
                            corporation_profile = self, 
                            status = status,
                            )

            else:
                apps = CorporationApplication.objects.filter(
                        corporation_profile = self,
                        )
        return apps

    def pending_applications(self, status=None):
        apps = self.get_applications((0,1))
        return apps

    def __str__(self):
        return "<Corporation Profile: %s>" % (self.corporation.name,)

    def __unicode__(self):
        return self.corporation.name

class AllianceProfile(models.Model):
    alliance = models.OneToOneField(Alliance, related_name='mgmt_profile')
    manager = models.ForeignKey(User, related_name='alliances_managed')
    director_group = models.OneToOneField(Group, related_name='executive_directors_of')
    api_mask = models.IntegerField(blank=True, null=True, default=None)
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "<Alliance Profile: %s>" % (self.alliance.alliance_name,)

    def has_director(self, user):
        try:
            return self.director_group in user.groups.all()
        except:
            # Safer this way.
            return False

class ApplicationMixin(models.Model):
    REJECTED = -1
    NEW = 0
    PENDING = 1
    APPROVED = 2
    PURGE = 3
    STATUS_CHOICES = (
            (REJECTED, 'Rejected'),
            (NEW, 'New'),
            (PENDING, 'Pending Review'),
            (APPROVED, 'Approved'),
            (PURGE, 'Pending Deletion'),
            )
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, editable=False)
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def reject(self):
        self.status = -1
        self.save()

    def pending(self):
        self.status = 1
        self.save()

    def approve(self):
        self.status = 2
        self.save()

    def mark_delete(self):
        self.status = 3
        self.save()

    def is_approved(self):
        return self.status == 2

    def is_pending(self):
        return self.status == 1

    def is_rejected(self):
        return self.status == -1

    def status_text(self):
        for status in self.STATUS_CHOICES:
            if status[0] is self.status:
                return status[1]

        return 'Unknown'

class Recommendation(models.Model):
    account = models.ForeignKey(Account, related_name='app_recommendations')
    application_type = models.ForeignKey(ContentType)
    application_id = models.PositiveIntegerField()
    application_obj = generic.GenericForeignKey('application_type', 'application_id')
    created_on = models.DateTimeField(auto_now_add=True)

class CorporationApplication(ApplicationMixin):
    character = models.OneToOneField(Character, related_name='corp_app')
    corporation_profile = models.ForeignKey(CorporationProfile, related_name='member_applications')
    created_by = models.ForeignKey(Account, related_name='corporation_applications')
    recommendations = generic.GenericRelation(Recommendation,
                                        content_type_field='application_type',
                                        object_id_field='application_id')
    reviewed_by = models.ForeignKey(Account, null=True, default=None, related_name='mbr_applications_reviewed')
    approved_by = models.ForeignKey(Account, null=True, default=None, related_name='mbr_applications_approved')
    rejected_by = models.ForeignKey(Account, null=True, default=None, related_name='mbr_applications_rejected')

    objects = managers.CorporationAppMgr()

    class Meta:
        unique_together = ('character', 'corporation_profile')

    def get_reddit(self):
        if self.corporation_profile.reddit_required:
            account = self.character.account
            reddit_account = account.reddit_account
            return reddit_account

        return None

    def __unicode__(self):
        return u"%s application for %s" % (self.corporation_profile, self.character)

class AllianceApplication(ApplicationMixin):
    corporation = models.OneToOneField(Corporation, related_name='alliance_application', unique=True)
    created_by = models.ForeignKey(Account, related_name='alliance_applications')
    recommendations = generic.GenericRelation(Recommendation,
                                        content_type_field='application_type',
                                        object_id_field='application_id')

    reviewed_by = models.ForeignKey(Account, null=True, default=None, related_name='crp_applications_reviewed')
    approved_by = models.ForeignKey(Account, null=True, default=None, related_name='crp_applications_approved')
    rejected_by = models.ForeignKey(Account, null=True, default=None, related_name='crp_applications_rejected')
    objects = managers.AllianceAppMgr()


# Signals because circular

@receiver(post_save, sender=APIKey)
def key_type_automater(sender, instance, created, **kwargs):
    key_type = instance.get_key_type()
    if key_type == 'Corporation':
        import sys
        conn = instance.get_api_connection()
        corpsheet = conn.corp.CorporationSheet()
        corpID = corpsheet.corporationID
        allianceID = corpsheet.allianceID

        print >> sys.stderr, "AllianceID: %s ; CorpID: %s; Dump %s" % (allianceID, corpID, corpsheet)

        def add_alliance(allianceID, group):
            try:
                auth_alliance = Alliance.objects.get(alliance_id = allianceID)
            except Alliance.DoesNotExist:
                # TODO: ACTUALLY discover the executor; likely easier done with the djangokb api handler.
                auth_alliance = Alliance(
                                    alliance_id = allianceID,
                                    alliance_name = corpsheet.allianceName,
                                    executor = auth_corp
                                )

            auth_alliance.save()
            alliance_profile = AllianceProfile(
                    alliance = auth_alliance,
                    manager = instance.account.user,
                    director_group = group,
                    api_mask = None,
                    )

            alliance_profile.save()
            return alliance_profile

        try:
            auth_corp = Corporation.objects.get(pk=corpID)

        except Corporation.DoesNotExist:
            auth_corp = Corporation(corp_id=corpID,name=corpsheet.corporationName)
            auth_corp.save()
            auth_corp.generate_logo(instance)

        try:
            corp_profile = CorporationProfile.objects.get(corporation=auth_corp)

        except CorporationProfile.DoesNotExist:
            group_name = "%s directors" % (auth_corp.name,)
            new_group = Group(name=group_name)
            new_group.save()
            corp_profile = CorporationProfile(
                        corporation = auth_corp,
                        manager = instance.account.user,
                        director_group = new_group,
                        api_mask = 8,
                        reddit_required = False,
                        alliance_profile = None,
                    )
            new_group.user_set.add(instance.account.user)
            new_group.save()

            if allianceID:
                alliance_profile = add_alliance(allianceID,new_group)
                corp_profile.alliance_profile = alliance_profile

            corp_profile.save()
