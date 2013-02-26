from celery.task import PeriodicTask
from datetime import timedelta
from django.conf import settings

from models import *

import praw

class ProcessRedditQueue(PeriodicTask):
    run_every = timedelta(minutes=5)

    def run(self, **kwargs):
        r = praw.Reddit(settings.REDDIT_USER_AGENT)

        r.login(settings.REDDIT_USER, settings.REDDIT_PASSWORD)

        new_since_last = r.user.get_unread(limit=None)

        invalid_messages = []

        for message in new_since_last:
            if message is None:
                continue

            if not message.subject.lower() == settings.REDDIT_AUTH_SUBJECT.lower():
                message.mark_unread()
                continue

            split_body = message.body.splitlines()

            if split_body[0] != "":
                if len(split_body[0]) == 64:
                    rc = RedditConfirmation.objects.get(key__exact = split_body[0])
                    if rc:
                        rc.confirm()
                    else:
                        invalid_messages.append(message)

                    continue

                else:
                    invalid_messages.append(message)

                    continue
            
            else:
                invalid_messages.append(message)

                continue


        for message in invalid_messages:
            message.reply("Invalid Auth Code.  Please make sure your code is the first and only line of your message.  Your subject was correct, so please use the same subject.  Do not reply to this message, it will not work.")
            message.mark_read()
