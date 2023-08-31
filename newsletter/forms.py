from django import forms

from organizations.models import Branch
from .models import Newsletter, BranchNewsletter


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ('text', 'active_last_month', 'active_last_week', 'active_last_day')




class BranchNewsletterForm(forms.ModelForm):
    pass

    class Meta:
        model = BranchNewsletter
        fields = ['branch']
        exclude = ('newsletter', )


class BranchNewsletterSelectForm(forms.Form):
    branch_newsletter = forms.ModelMultipleChoiceField(
        queryset=Branch.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )