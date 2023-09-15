from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import LoginForm

class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        if self.request.user.role == 1:
            return reverse_lazy('')
        elif self.request.user.role == 2:
            return reverse_lazy('organization:branch_list')
        elif self.request.user.role == 3:
            return reverse_lazy('customer_request:employee_index')



class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Вы вышли из системы. Войдите снова, чтобы продолжить.')
        return super().dispatch(request, *args, **kwargs)
