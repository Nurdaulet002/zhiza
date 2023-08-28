from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('list/', views.CustomerListView.as_view(),
         name='customer_list'),
    path('export/', views.ExportCustomersView.as_view(),
         name='export_customers'),

]