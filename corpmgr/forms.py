from django import forms
from models import CorporationApplication, CorporationProfile
from eveauth.models import Corporation, Character

class CorpApplicationForm(forms.ModelForm):

    character = forms.ModelChoiceField(queryset=Character.objects.all())
    corporation_profile = forms.ModelChoiceField(queryset=CorporationProfile.objects.all())

    class Meta:
        model = CorporationApplication
        exclude = (
                    'created_by',
                    'recommendations',
                    'reviewed_by',
                    'approved_by',
                    'rejected_by',
                  )

    def __init__(self, *args, **kwargs):

        applying_user = kwargs.pop('user')
        super(CorpApplicationForm, self).__init__(*args, **kwargs)

        self.fields['character'].queryset = Character.objects.filter(
                         account=applying_user.get_profile()
                )

    def clean(self):
        cleaned_data = super(CorpApplicationForm, self).clean()

        key_mask = cleaned_data.get("character").api_key.get_key_mask()
        needed_mask = cleaned_data.get("corporation_profile").api_mask

        if (key_mask & needed_mask) == needed_mask:
            return cleaned_data
        else:
            raise forms.ValidationError("Your API key does not meet the corporate requirements of that corporation.")
