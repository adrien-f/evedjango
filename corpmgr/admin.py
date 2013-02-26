from django.contrib import admin
from models import *

class CorpProfileAdmin(admin.ModelAdmin):
    list_display = (
            'corporation',
            'manager',
            'director_group',
            'alliance_profile',
            'reddit_required',
            )

class AllianceProfileAdmin(admin.ModelAdmin):
    list_display = (
            'alliance',
            'manager',
            'director_group',
            )

class CorpAppAdmin(admin.ModelAdmin):
    list_display = (
            'character',
            'corporation_profile',
            )
           


admin.site.register(CorporationProfile, CorpProfileAdmin)
admin.site.register(AllianceProfile, AllianceProfileAdmin)
admin.site.register(CorporationApplication, CorpAppAdmin)
