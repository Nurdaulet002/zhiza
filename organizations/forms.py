from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.hashers import check_password

from accounts.models import CustomUser
from constants import USERTYPE_MANAGER, USERTYPE_EMPLOYEE
from organizations.models import Branch, CompanyUser



class BranchForm(forms.ModelForm):

    class Meta:
        model = Branch
        fields = ['title', 'address', 'cards_number']


class CustomUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'first_name', 'last_name', 'branch', 'role']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            company_user = CompanyUser.objects.get(user=user)
            if company_user:
                allowed_branches = company_user.company.branches.all()
                self.fields['branch'].queryset = allowed_branches
            # Ограничьте выбор ролей только Админ и Работник
            self.fields['role'].choices = [
                (USERTYPE_MANAGER, 'Админ'),
                (USERTYPE_EMPLOYEE, 'Работник'),
            ]

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Пользователь с именем {username} уже существует.')
        return username





class CustomUserUpdateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    old_password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'branch', 'role']  # other fields

    # This is just for the admin form view
    def clean_password(self):
        return ReadOnlyPasswordHashField().clean(self.cleaned_data.get('password'))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            company_user = CompanyUser.objects.get(user=user)
            if company_user:
                allowed_branches = company_user.company.branches.all()
                self.fields['branch'].queryset = allowed_branches
            # Ограничьте выбор ролей только Админ и Работник
            self.fields['role'].choices = [
                (USERTYPE_MANAGER, 'Админ'),
                (USERTYPE_EMPLOYEE, 'Работник'),
            ]

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        user = self.instance  # Получаем текущего пользователя

        # Проверяем, совпадает ли введенный старый пароль с фактическим старым паролем пользователя
        if old_password and not check_password(old_password, user.password):
            raise forms.ValidationError(f'Старый пароль неверен.')

        return old_password


