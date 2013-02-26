from django.http import Http404, HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from datetime import datetime

from django.views.generic.base import RedirectView, View, TemplateResponseMixin
from django.views.generic.edit import FormView

from account.utils import default_redirect, user_display

from django.template import RequestContext

from eveauth.tasks import update_characters

from models import RedditAccount, RedditConfirmation
from forms import RedditAccountForm

import os

class OwnerDetailsView(FormView):
    pass

class RedditConfirmationView(OwnerDetailsView):
    model = RedditAccount
    form_class = RedditAccountForm
    template_name = "vreddit/confirmation.html"

    def form_valid(self, form):
        u = self.request.user
        if u.is_authenticated():
            reddit_account = form.save(commit=False)
            reddit_account.account = u.get_profile()
            # Force it to create one
            reddit_account.save()
            confirmation = reddit_account.get_confirmation()
            confirmation.sent = timezone.now()
            confirmation.save()
            self.object = reddit_account

            return super(RedditConfirmationView, self).form_valid(form)

        raise HttpResponseForbidden

    def form_invalid(self, form):
        messages.error(self.request, mark_safe("Your reddit account is invalid.  Go away, nerd."))
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('reddit_confirmation')

    def get(self, request):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        user = request.user
        if not user.is_authenticated():
            messages.error(self.request, "You're not logged in.  You can't do that if you don't have an account and/or aren't logged in.  Pretty silly if you ask me.")
            return redirect("/account/login")

        account = user.get_profile()

        try:
            reddit_account = RedditAccount.objects.get(account=account)
        except:
            reddit_account = None

        if reddit_account:
            if reddit_account.verified:
                messages.error(self.request, "You're already verified, you can't be verified again.  Pretty silly if you ask me.")
                return redirect("/")

            confirmation = reddit_account.get_confirmation(create=False)

            context = self.get_context_data(form=form)

            if confirmation:
                if confirmation.sent and confirmation.key_expired():
                    messages.error("You apparently had an expired request and it has been deleted.  Please try again.")
                    confirmation.delete()
                    account.reddit_account.delete()
                    rc = RequestContext(request, context)
                    return self.render_to_response(rc)

                has_confirmation = True
            else:
                has_confirmation = False

            add_context = {
                        'has_confirmation': has_confirmation,
                        'confirmation': confirmation,
                        'reddit_account': reddit_account,
                        'reddit_subject': settings.REDDIT_AUTH_SUBJECT,
                        'site_reddit_user': settings.REDDIT_USER,
                        }
            context = dict(context.items() + add_context.items())
            rc = RequestContext(request, context)

            return self.render_to_response(rc)

        else:
            context = self.get_context_data(form=form)
            rc = RequestContext(request, context)

            return self.render_to_response(rc)

