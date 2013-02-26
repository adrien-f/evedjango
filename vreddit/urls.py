from django.conf.urls import patterns, include, url

from models import *
from forms import *
from views import *

urlpatterns = patterns("vreddit.views",

        url(r'^account/$', RedditConfirmationView.as_view(), name="reddit_confirmation"),
)
