from django.urls import path
from . import views

app_name = 'organization'

urlpatterns = [
    path('feedback/list/', views.FeedbackListView.as_view(),
         name='feedback_list'),
    path('branch/detail/', views.BranchDetailView.as_view(),
         name='branch_detail'),
    path('report/', views.ReportView.as_view(),
         name='report'),

    path('branch/list/', views.BranchListView.as_view(), name='branch_list'),
    path('branch/create/', views.BranchCreateView.as_view(), name='branch_create'),
    path('branch/<int:pk>/update/', views.BranchUpdateView.as_view(), name='branch_update'),
    path('branch/<int:pk>/delete/', views.BranchDeleteView.as_view(), name='branch_delete'),

    path('employee/list/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employee/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employee/<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employee/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),

]