from rest_framework import serializers
from .models import Campaign, QuoteView, QuoteClick, CampaignView, CampaignClick


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ['id', 'name', 'client_name', 'text', 'url', 'sns_url', 'start_date', 'end_date']


class QuoteViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteView
        fields = ['quote', 'client_id', 'viewed_at']


class QuoteClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteClick
        fields = ['quote', 'client_id', 'action', 'clicked_at']


class CampaignViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignView
        fields = ['campaign', 'client_id', 'viewed_at']


class CampaignClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignClick
        fields = ['campaign', 'client_id', 'action', 'clicked_at']
