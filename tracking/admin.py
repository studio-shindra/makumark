from django.contrib import admin
from .models import Campaign, QuoteView, QuoteClick, CampaignView, CampaignClick


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'client_name', 'start_date', 'end_date', 'created_at']
    list_filter = ['start_date', 'end_date', 'created_at']
    search_fields = ['name', 'client_name', 'text']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']


@admin.register(QuoteView)
class QuoteViewAdmin(admin.ModelAdmin):
    list_display = ['quote', 'client_id', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['quote__text', 'client_id']
    date_hierarchy = 'viewed_at'
    ordering = ['-viewed_at']
    readonly_fields = ['quote', 'client_id', 'viewed_at']


@admin.register(QuoteClick)
class QuoteClickAdmin(admin.ModelAdmin):
    list_display = ['quote', 'action', 'client_id', 'clicked_at']
    list_filter = ['action', 'clicked_at']
    search_fields = ['quote__text', 'client_id']
    date_hierarchy = 'clicked_at'
    ordering = ['-clicked_at']
    readonly_fields = ['quote', 'client_id', 'action', 'clicked_at']


@admin.register(CampaignView)
class CampaignViewAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'client_id', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['campaign__name', 'client_id']
    date_hierarchy = 'viewed_at'
    ordering = ['-viewed_at']
    readonly_fields = ['campaign', 'client_id', 'viewed_at']


@admin.register(CampaignClick)
class CampaignClickAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'action', 'client_id', 'clicked_at']
    list_filter = ['action', 'clicked_at']
    search_fields = ['campaign__name', 'client_id']
    date_hierarchy = 'clicked_at'
    ordering = ['-clicked_at']
    readonly_fields = ['campaign', 'client_id', 'action', 'clicked_at']
