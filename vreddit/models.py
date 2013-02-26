from django.db import models
from django.conf import settings
from account.models import Account
from datetime import datetime, timedelta
import eveapi, os, Image, managers

from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sites.models import Site

from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _

from account.utils import random_token

from . import signals

class RedditAccount(models.Model):

    account = models.OneToOneField(Account, primary_key=True, related_name='reddit_account')
    reddit_login = models.CharField(max_length=128, unique=settings.REDDIT_LOGIN_UNIQUE)
    verified = models.BooleanField(default=False)
    
    objects = managers.RedditAccountManager()
    
    class Meta:
        verbose_name = _("reddit account")
        verbose_name_plural = _("reddit accounts")
        if not settings.REDDIT_LOGIN_UNIQUE:
            unique_together = [("account", "reddit_login")]
    
    def __unicode__(self):
        return u"%s (%s)" % (self.reddit_login, self.account)
    
    def associated_characters(self):
        charlist = []
        apikeys = self.account.apikeys.all()
        for apikey in apikeys:
            charlist += apikey.get_characters().all()

        return ", ".join([char.character_name for char in charlist])
    
    associated_characters.short_description = "Characters"

    def get_confirmation(self, create=True):
        try:
            confirmation = self.reddit_confirmation.get()
        except:
            confirmation = None

        if not confirmation and create: 
            confirmation = RedditConfirmation.create(self)
            confirmation.sent = timezone.now()
            confirmation.save()

        return confirmation


class RedditConfirmation(models.Model):
    
    reddit_account = models.ForeignKey(RedditAccount, related_name='reddit_confirmation')
    created = models.DateTimeField(default=timezone.now())
    sent = models.DateTimeField(null=True)
    key = models.CharField(max_length=64, unique=True)
    
    objects = managers.RedditConfirmationManager()
    
    class Meta:
        verbose_name = _("reddit confirmation")
        verbose_name_plural = _("reddit confirmations")
    
    def __unicode__(self):
        return u"reddit confirmation for %s" % self.reddit_account
    
    @classmethod
    def create(cls, reddit_account):
        key = random_token([reddit_account.reddit_login])
        return cls._default_manager.create(reddit_account=reddit_account, key=key)
    
    def key_expired(self):
        expiration_date = self.sent + timedelta(days=10)
        #expiration_date = self.sent + timedelta(days=settings.REDDIT_CONFIRMATION_EXPIRE_DAYS)
        return expiration_date <= timezone.now()
    key_expired.boolean = True
    
    def confirm(self):
        if not self.key_expired() and not self.reddit_account.verified:
            reddit_account = self.reddit_account
            reddit_account.verified = True
            reddit_account.save()
            #signals.reddit_account.send(sender=self.__class__, reddit_account=reddit_account)
            return reddit_account
    

