from django import forms

from organizations.models import Branch
from raffle_prizes.models import RafflePrize

from django_select2.forms import Select2MultipleWidget



class RafflePrizeForm(forms.ModelForm):
    class Meta:
        model = RafflePrize
        fields = ('title', )
        exclude = ('company', )


class RafflePrizeSettingForm(forms.ModelForm):
    class Meta:
        model = RafflePrize
        fields = ('message_winner', 'number_winners', 'date_start', 'date_end', 'comment', 'image')


class ParticipatingBranchSelectForm(forms.Form):
    participating_branches = forms.ModelMultipleChoiceField(
        queryset=Branch.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )