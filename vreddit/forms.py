from django import forms
from models import RedditAccount, RedditConfirmation
from django.conf import settings

import praw

class RedditAccountForm(forms.ModelForm):
    class Meta:
        model = RedditAccount
        exclude = ('account', 'verified')

    def clean(self):
        cleaned_data = super(RedditAccountForm, self).clean()

        reddit_login = cleaned_data.get("reddit_login")

        r = praw.Reddit(settings.REDDIT_USER_AGENT)
        redditor = r.get_redditor(reddit_login)

        if not redditor:
            raise forms.ValidationError("Invalid Reddit User.")
        
        return cleaned_data
