from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import LoginForm

class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        if self.request.user.role == 1:
            return reverse_lazy('')
        elif self.request.user.role == 2:
            return reverse_lazy('newsletter:draft_list')
        elif self.request.user.role == 3:
            return reverse_lazy('customer_request:employee_index')
