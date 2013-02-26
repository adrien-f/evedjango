from django.db import models, IntegrityError

class RedditConfirmationManager(models.Manager):
    def delete_expired_confirmations(self):
        for confirmation in self.all():
            if confirmation.key_expired():
                confirmation.delete()


class RedditAccountManager(models.Manager):

    def add_reddit_account(self, account, reddit_login, **kwargs):
        confirm = kwargs("confirm", False)

        try:
            reddit_account = self.create(account=account, reddit_login=reddit_login, **kwargs)
        except IntegrityError:
            return None
        else:
            if confirm and not reddit_account.verified:
                reddit_account.send_confirmation()
            return reddit_account


    def get_users_for(self, reddit_login):
        return [reddit.account.user for reddit in self.filter(verified=True, reddit_login=reddit_login)]
