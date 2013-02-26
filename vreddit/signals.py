#
import django.dispatch

reddit_confirmed = django.dispatch.Signal(providing_args=["reddit_login"])
