from django import forms

from accounts.models import CustomUser
from organizations.models import Branch


class BranchForm(forms.ModelForm):

    class Meta:
        model = Branch
        fields = ['title', 'address', 'cards_number']


class CustomUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'first_name', 'last_name', 'branch', 'role']


from django.contrib.auth.forms import ReadOnlyPasswordHashField


class CustomUserUpdateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    old_password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'branch', 'role']  # other fields

    # This is just for the admin form view
    def clean_password(self):
        return ReadOnlyPasswordHashField().clean(self.cleaned_data.get('password'))


