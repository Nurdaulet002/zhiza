from django.urls import path
from . import views

app_name = 'customer_request'

urlpatterns = [
    path('index/', views.EmployeeIndexView.as_view(),
         name='employee_index'),
    path('send/message', views.SendMessageView.as_view(),
         name='send_message'),
    path('webhook/whatsapp', views.webhookWhatsApp,
         name='webhook_whatsapp'),
]