from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    path('create/', views.NewsletterCreateView.as_view(),
         name='create'),
    path('detail/summary/<int:pk>', views.NewsletterDetailSummaryView.as_view(),
         name='detail_summary'),
    path('detail/message/<int:pk>', views.NewsletterDetailMessageView.as_view(),
         name='detail_message'),
    path('detail/message/create/<int:pk>', views.NewsletterMessageCreateUpdateView.as_view(),
         name='message_create'),
    path('draft/recipient/create/update/<int:pk>', views.RecipientDataBaseCreateUpdateView.as_view(),
         name='recipient_create_update'),
    path('draft/list/', views.DraftListView.as_view(),
         name='draft_list'),
    path('under/review/list/', views.UnderReviewListView.as_view(),
         name='under_review_list'),
    path('under/review/confirm/<int:pk>', views.UnderReviewConfirmView.as_view(),
         name='under_review_confirm'),
    path('under/review/cancel/confirm/<int:pk>', views.UnderReviewCancelConfirmView.as_view(),
         name='under_review_cancel_confirm'),
    path('ready/to/start/list', views.ReadyToStartListView.as_view(),
         name='ready_to_start_list'),
    path('start/newsletter', views.StartNewsletterView.as_view(),
         name='start_newsletter'),
    path('in_progress/list', views.InProgressListView.as_view(),
         name='in_progress_list'),
    path('completed/list', views.CompletedListView.as_view(),
         name='completed_list'),

]