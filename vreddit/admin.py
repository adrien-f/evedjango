from django.contrib import admin

from models import RedditAccount, RedditConfirmation

class RedditAccountAdmin(admin.ModelAdmin):
    list_display = ( 
            'reddit_login',
            'account',
            'verified',
            'associated_characters',
            )

class RedditConfirmationAdmin(admin.ModelAdmin):
    pass

admin.site.register(RedditAccount, RedditAccountAdmin)
admin.site.register(RedditConfirmation, RedditConfirmationAdmin)
