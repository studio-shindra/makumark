from django.urls import path
from . import views

urlpatterns = [
    path('campaigns/active/', views.active_campaigns, name='active_campaigns'),
    path('campaigns/view/', views.track_campaign_view, name='track_campaign_view'),
    path('campaigns/click/', views.track_campaign_click, name='track_campaign_click'),
    path('quotes/view/', views.track_quote_view, name='track_quote_view'),
    path('quotes/click/', views.track_quote_click, name='track_quote_click'),
    path('stats/overview/', views.stats_overview, name='stats_overview'),
]
