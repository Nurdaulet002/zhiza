from django.urls import path
from . import views

app_name = 'raffle_prizes'

urlpatterns = [
    path('list/', views.RafflePrizeListView.as_view(),
         name='raffle_prize_list'),
    path('create/', views.RufflePrizeCreateView.as_view(),
         name='create'),
    path('update/<pk>', views.RufflePrizeUpdateView.as_view(),
         name='update'),
    path('delete/<pk>', views.RufflePrizeDeleteView.as_view(),
         name='delete'),
    path('detail/settings/<pk>', views.RufflePrizeSettingView.as_view(),
         name='settings'),
    path('detail/settings/form/<int:pk>', views.RufflePrizeSettingFormView.as_view(),
         name='settings_form'),
    path('detail/participating/branch/list/<int:pk>', views.ParticipatingBranchListView.as_view(),
         name='participating_branch_list'),
    path('detail/participating/branch/save', views.ParticipatingBranchSaveView.as_view(),
         name='participating_branch_save'),
    path('detail/participating/branch/winners/<int:pk>', views.WinnersDetailView.as_view(),
         name='participating_branch_winners'),
    path('detail/participating/branch/choice/winner/<int:pk>', views.ChoiceRandomWinner.as_view(),
         name='participating_branch_choice_winner'),
    path('search/code', views.PromoCodeView.as_view(),
         name='search_promocode'),
    path('search/code/<promocode>', views.PromoCodeView.as_view(),
         name='search_promocode'),
    path('generate/code', views.GenerateCode.as_view(),
         name='generate_code'),
    path('checking/sms/<promocode>', views.CheckingSMSView.as_view(),
         name='checking_sms'),

]