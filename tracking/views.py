from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from datetime import date
from .models import Campaign, QuoteView, QuoteClick, CampaignView, CampaignClick
from .serializers import (
    CampaignSerializer,
    QuoteViewSerializer,
    QuoteClickSerializer,
    CampaignViewSerializer,
    CampaignClickSerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def active_campaigns(request):
    """今日有効なキャンペーン一覧"""
    today = date.today()
    campaigns = Campaign.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    )
    serializer = CampaignSerializer(campaigns, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def track_campaign_view(request):
    """Campaign 表示を記録"""
    campaign_id = request.data.get('campaign_id')
    client_id = request.data.get('client_id')
    
    if not campaign_id or not client_id:
        return Response(
            {'error': 'campaign_id and client_id are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        campaign = Campaign.objects.get(pk=campaign_id)
        CampaignView.objects.create(
            campaign=campaign,
            client_id=client_id
        )
        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)
    except Campaign.DoesNotExist:
        return Response(
            {'error': 'Campaign not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def track_campaign_click(request):
    """Campaign クリックを記録"""
    campaign_id = request.data.get('campaign_id')
    client_id = request.data.get('client_id')
    action = request.data.get('action', 'official')
    
    if not campaign_id or not client_id:
        return Response(
            {'error': 'campaign_id and client_id are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        campaign = Campaign.objects.get(pk=campaign_id)
        CampaignClick.objects.create(
            campaign=campaign,
            client_id=client_id,
            action=action
        )
        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)
    except Campaign.DoesNotExist:
        return Response(
            {'error': 'Campaign not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def track_quote_view(request):
    """Quote 表示を記録"""
    from quotes.models import Quote
    
    quote_id = request.data.get('quote_id')
    client_id = request.data.get('client_id')
    
    if not quote_id or not client_id:
        return Response(
            {'error': 'quote_id and client_id are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        quote = Quote.objects.get(pk=quote_id)
        QuoteView.objects.create(
            quote=quote,
            client_id=client_id
        )
        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)
    except Quote.DoesNotExist:
        return Response(
            {'error': 'Quote not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def track_quote_click(request):
    """Quote 内アクション（Wiki/Amazon/Share）を記録"""
    from quotes.models import Quote
    
    quote_id = request.data.get('quote_id')
    client_id = request.data.get('client_id')
    action = request.data.get('action')
    
    if not quote_id or not client_id or not action:
        return Response(
            {'error': 'quote_id, client_id, and action are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if action not in ['wiki', 'amazon', 'share']:
        return Response(
            {'error': 'action must be wiki, amazon, or share'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        quote = Quote.objects.get(pk=quote_id)
        QuoteClick.objects.create(
            quote=quote,
            client_id=client_id,
            action=action
        )
        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)
    except Quote.DoesNotExist:
        return Response(
            {'error': 'Quote not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def stats_overview(request):
    """統計サマリー（日別）"""
    target_date = request.query_params.get('date')
    
    if target_date:
        try:
            target = date.fromisoformat(target_date)
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        target = date.today()
    
    # その日の開始・終了時刻
    start = timezone.datetime.combine(target, timezone.datetime.min.time())
    end = timezone.datetime.combine(target, timezone.datetime.max.time())
    
    # Quote stats
    quote_views = QuoteView.objects.filter(viewed_at__range=(start, end)).count()
    quote_clicks = QuoteClick.objects.filter(clicked_at__range=(start, end)).count()
    
    # Campaign stats
    campaign_views = CampaignView.objects.filter(viewed_at__range=(start, end)).count()
    campaign_clicks = CampaignClick.objects.filter(clicked_at__range=(start, end)).count()
    
    # CTR 計算
    ctr_quote = (quote_clicks / quote_views * 100) if quote_views > 0 else 0
    ctr_campaign = (campaign_clicks / campaign_views * 100) if campaign_views > 0 else 0
    
    return Response({
        'date': target.isoformat(),
        'total_quote_views': quote_views,
        'total_quote_clicks': quote_clicks,
        'total_campaign_views': campaign_views,
        'total_campaign_clicks': campaign_clicks,
        'ctr_quote': round(ctr_quote, 2),
        'ctr_campaign': round(ctr_campaign, 2),
    })
