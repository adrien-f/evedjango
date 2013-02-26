from django.contrib.auth.decorators import user_passes_test

def character_required():
    """ Requires user to have a default character defined."""

    def has_character(u):
        if u.is_authenticated():
            if bool(u.default_character) | u.is_superuser:
                return True
        return False
    return user_passes_test(has_character)
