# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CorporationProfile'
        db.create_table(u'corpmgr_corporationprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('corporation', self.gf('django.db.models.fields.related.OneToOneField')(related_name='mgmt_profile', unique=True, to=orm['evedjango.Corporation'])),
            ('manager', self.gf('django.db.models.fields.related.ForeignKey')(related_name='corps_managed', unique=True, to=orm['auth.User'])),
            ('director_group', self.gf('django.db.models.fields.related.OneToOneField')(related_name='directors_of', unique=True, to=orm['auth.Group'])),
            ('api_mask', self.gf('django.db.models.fields.IntegerField')()),
            ('reddit_required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('alliance_profile', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='member_corp_profiles', null=True, to=orm['corpmgr.AllianceProfile'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'corpmgr', ['CorporationProfile'])

        # Adding unique constraint on 'CorporationProfile', fields ['corporation', 'alliance_profile']
        db.create_unique(u'corpmgr_corporationprofile', ['corporation_id', 'alliance_profile_id'])

        # Adding model 'AllianceProfile'
        db.create_table(u'corpmgr_allianceprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alliance', self.gf('django.db.models.fields.related.OneToOneField')(related_name='mgmt_profile', unique=True, to=orm['evedjango.Alliance'])),
            ('manager', self.gf('django.db.models.fields.related.ForeignKey')(related_name='alliances_managed', to=orm['auth.User'])),
            ('director_group', self.gf('django.db.models.fields.related.OneToOneField')(related_name='executive_directors_of', unique=True, to=orm['auth.Group'])),
            ('api_mask', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'corpmgr', ['AllianceProfile'])

        # Adding model 'Recommendation'
        db.create_table(u'corpmgr_recommendation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='app_recommendations', to=orm['auth.User'])),
            ('application_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('application_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'corpmgr', ['Recommendation'])

        # Adding model 'CorporationApplication'
        db.create_table(u'corpmgr_corporationapplication', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('character', self.gf('django.db.models.fields.related.OneToOneField')(related_name='corp_app', unique=True, to=orm['evedjango.Character'])),
            ('corporation_profile', self.gf('django.db.models.fields.related.ForeignKey')(related_name='member_applications', to=orm['corpmgr.CorporationProfile'])),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='corporation_applications', to=orm['auth.User'])),
            ('reviewed_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='mbr_applications_reviewed', null=True, to=orm['auth.User'])),
            ('approved_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='mbr_applications_approved', null=True, to=orm['auth.User'])),
            ('rejected_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='mbr_applications_rejected', null=True, to=orm['auth.User'])),
        ))
        db.send_create_signal(u'corpmgr', ['CorporationApplication'])

        # Adding unique constraint on 'CorporationApplication', fields ['character', 'corporation_profile']
        db.create_unique(u'corpmgr_corporationapplication', ['character_id', 'corporation_profile_id'])

        # Adding model 'AllianceApplication'
        db.create_table(u'corpmgr_allianceapplication', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('corporation', self.gf('django.db.models.fields.related.OneToOneField')(related_name='alliance_application', unique=True, to=orm['evedjango.Corporation'])),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='alliance_applications', to=orm['auth.User'])),
            ('reviewed_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='crp_applications_reviewed', null=True, to=orm['auth.User'])),
            ('approved_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='crp_applications_approved', null=True, to=orm['auth.User'])),
            ('rejected_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='crp_applications_rejected', null=True, to=orm['auth.User'])),
        ))
        db.send_create_signal(u'corpmgr', ['AllianceApplication'])


    def backwards(self, orm):
        # Removing unique constraint on 'CorporationApplication', fields ['character', 'corporation_profile']
        db.delete_unique(u'corpmgr_corporationapplication', ['character_id', 'corporation_profile_id'])

        # Removing unique constraint on 'CorporationProfile', fields ['corporation', 'alliance_profile']
        db.delete_unique(u'corpmgr_corporationprofile', ['corporation_id', 'alliance_profile_id'])

        # Deleting model 'CorporationProfile'
        db.delete_table(u'corpmgr_corporationprofile')

        # Deleting model 'AllianceProfile'
        db.delete_table(u'corpmgr_allianceprofile')

        # Deleting model 'Recommendation'
        db.delete_table(u'corpmgr_recommendation')

        # Deleting model 'CorporationApplication'
        db.delete_table(u'corpmgr_corporationapplication')

        # Deleting model 'AllianceApplication'
        db.delete_table(u'corpmgr_allianceapplication')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'corpmgr.allianceapplication': {
            'Meta': {'object_name': 'AllianceApplication'},
            'approved_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'crp_applications_approved'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'corporation': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'alliance_application'", 'unique': 'True', 'to': u"orm['evedjango.Corporation']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alliance_applications'", 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'rejected_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'crp_applications_rejected'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'reviewed_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'crp_applications_reviewed'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'corpmgr.allianceprofile': {
            'Meta': {'object_name': 'AllianceProfile'},
            'alliance': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'mgmt_profile'", 'unique': 'True', 'to': u"orm['evedjango.Alliance']"}),
            'api_mask': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'director_group': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'executive_directors_of'", 'unique': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alliances_managed'", 'to': u"orm['auth.User']"})
        },
        u'corpmgr.corporationapplication': {
            'Meta': {'unique_together': "(('character', 'corporation_profile'),)", 'object_name': 'CorporationApplication'},
            'approved_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'mbr_applications_approved'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'character': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'corp_app'", 'unique': 'True', 'to': u"orm['evedjango.Character']"}),
            'corporation_profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'member_applications'", 'to': u"orm['corpmgr.CorporationProfile']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corporation_applications'", 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'rejected_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'mbr_applications_rejected'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'reviewed_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'mbr_applications_reviewed'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'corpmgr.corporationprofile': {
            'Meta': {'unique_together': "(('corporation', 'alliance_profile'),)", 'object_name': 'CorporationProfile'},
            'alliance_profile': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'member_corp_profiles'", 'null': 'True', 'to': u"orm['corpmgr.AllianceProfile']"}),
            'api_mask': ('django.db.models.fields.IntegerField', [], {}),
            'corporation': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'mgmt_profile'", 'unique': 'True', 'to': u"orm['evedjango.Corporation']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'director_group': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'directors_of'", 'unique': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corps_managed'", 'unique': 'True', 'to': u"orm['auth.User']"}),
            'reddit_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'corpmgr.recommendation': {
            'Meta': {'object_name': 'Recommendation'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'app_recommendations'", 'to': u"orm['auth.User']"}),
            'application_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'application_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'eve_db.chrfaction': {
            'Meta': {'ordering': "['id']", 'object_name': 'ChrFaction'},
            'corporation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'faction_set'", 'null': 'True', 'to': "orm['eve_db.CrpNPCCorporation']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'icon_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'size_factor': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'solar_system': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'faction_set'", 'null': 'True', 'to': "orm['eve_db.MapSolarSystem']"}),
            'station_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'station_system_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'eve_db.chrrace': {
            'Meta': {'ordering': "['id']", 'object_name': 'ChrRace'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'icon_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'short_description': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'eve_db.crpnpccorporation': {
            'Meta': {'ordering': "['id']", 'object_name': 'CrpNPCCorporation'},
            'border_systems': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'corridor_systems': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enemy_corp': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'enemy_of_set'", 'null': 'True', 'to': "orm['eve_db.CrpNPCCorporation']"}),
            'extent': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'faction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve_db.ChrFaction']", 'null': 'True', 'blank': 'True'}),
            'friendly_corp': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'friendly_with_set'", 'null': 'True', 'to': "orm['eve_db.CrpNPCCorporation']"}),
            'fringe_systems': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'hub_systems': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'icon_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'initial_share_price': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'investor1': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'invested1_set'", 'null': 'True', 'to': "orm['eve_db.CrpNPCCorporation']"}),
            'investor1_shares': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'investor2': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'invested2_set'", 'null': 'True', 'to': "orm['eve_db.CrpNPCCorporation']"}),
            'investor2_shares': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'investor3': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'invested3_set'", 'null': 'True', 'to': "orm['eve_db.CrpNPCCorporation']"}),
            'investor3_shares': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'investor4': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'invested4_set'", 'null': 'True', 'to': "orm['eve_db.CrpNPCCorporation']"}),
            'investor4_shares': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_security': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'public_share_percent': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'size_factor': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'solar_system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve_db.MapSolarSystem']", 'null': 'True', 'blank': 'True'}),
            'station_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'station_system_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'stations_are_scattered': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'eve_db.invcategory': {
            'Meta': {'ordering': "['id']", 'object_name': 'InvCategory'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'icon_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'eve_db.invgroup': {
            'Meta': {'ordering': "['id']", 'object_name': 'InvGroup'},
            'allow_anchoring': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_manufacture': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_recycle': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve_db.InvCategory']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'icon_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'is_anchored': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_fittable_non_singleton': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'use_base_price': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'eve_db.invmarketgroup': {
            'Meta': {'ordering': "['id']", 'object_name': 'InvMarketGroup'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300012', 'null': 'True', 'blank': 'True'}),
            'has_items': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'icon_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve_db.InvMarketGroup']", 'null': 'True', 'blank': 'True'})
        },
        'eve_db.invtype': {
            'Meta': {'ordering': "['id']", 'object_name': 'InvType'},
            'base_price': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'capacity': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'chance_of_duplicating': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve_db.InvGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'market_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve_db.InvMarketGroup']", 'null': 'True', 'blank': 'True'}),
            'mass': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'portion_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve_db.ChrRace']", 'null': 'True', 'blank': 'True'}),
            'volume': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'eve_db.mapconstellation': {
            'Meta': {'ordering': "['id']", 'object_name': 'MapConstellation'},
            'faction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve_db.ChrFaction']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve_db.MapRegion']", 'null': 'True', 'blank': 'True'}),
            'sovereignty_grace_start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sovereignty_start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'x': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'x_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'x_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'z': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'z_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'z_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'eve_db.mapregion': {
            'Meta': {'ordering': "['id']", 'object_name': 'MapRegion'},
            'faction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve_db.ChrFaction']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'x': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'x_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'x_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'z': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'z_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'z_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'eve_db.mapsolarsystem': {
            'Meta': {'ordering': "['id']", 'object_name': 'MapSolarSystem'},
            'constellation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve_db.MapConstellation']", 'null': 'True', 'blank': 'True'}),
            'faction': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'solarsystem_set'", 'null': 'True', 'to': "orm['eve_db.ChrFaction']"}),
            'has_interconstellational_link': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_interregional_link': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'is_border_system': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_corridor_system': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_fringe_system': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_hub_system': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_international': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'luminosity': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve_db.MapRegion']", 'null': 'True', 'blank': 'True'}),
            'security_class': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'security_level': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'sovereignty_level': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sovereignty_start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sun_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve_db.InvType']", 'null': 'True', 'blank': 'True'}),
            'x': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'x_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'x_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'y_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'z': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'z_max': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'z_min': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'evedjango.alliance': {
            'Meta': {'object_name': 'Alliance'},
            'api_keys': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'evedjango_alliance_entities'", 'symmetrical': 'False', 'to': u"orm['evedjango.APIKeyInfo']"}),
            'faction': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'militia_member_alliances'", 'null': 'True', 'to': "orm['eve_db.ChrFaction']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'evedjango.apikey': {
            'Meta': {'unique_together': "(('id', 'site'),)", 'object_name': 'APIKey'},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_api_keys'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'site_api_keys'", 'to': u"orm['sites.Site']"}),
            'vcode': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'evedjango.apikeyinfo': {
            'Meta': {'object_name': 'APIKeyInfo'},
            'access_mask': ('django.db.models.fields.IntegerField', [], {}),
            'api_key': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'info'", 'unique': 'True', 'to': u"orm['evedjango.APIKey']"}),
            'cached_until': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'expires_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_type': ('django.db.models.fields.CharField', [], {'default': "'UN'", 'max_length': '2', 'db_index': 'True'})
        },
        u'evedjango.character': {
            'Meta': {'object_name': 'Character'},
            'alliance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['evedjango.Alliance']", 'null': 'True'}),
            'api_keys': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'evedjango_character_entities'", 'symmetrical': 'False', 'to': u"orm['evedjango.APIKeyInfo']"}),
            'corporation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['evedjango.Corporation']"}),
            'faction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eve_db.ChrFaction']", 'null': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'evedjango.corporation': {
            'Meta': {'object_name': 'Corporation'},
            'alliance': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'member_corps'", 'null': 'True', 'to': u"orm['evedjango.Alliance']"}),
            'api_keys': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'evedjango_corporation_entities'", 'symmetrical': 'False', 'to': u"orm['evedjango.APIKeyInfo']"}),
            'faction': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'militia_member_corps'", 'null': 'True', 'to': "orm['eve_db.ChrFaction']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['corpmgr']