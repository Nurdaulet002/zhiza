from django.urls import path
from . import views

app_name = 'organization'

urlpatterns = [
    path('branch/list/', views.BranchListView.as_view(),
         name='branch_list'),
    path('branch/detail/<pk>', views.BranchDetailView.as_view(),
         name='branch_detail'),
]