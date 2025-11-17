from django.db import models
from quotes.models import Quote


class Campaign(models.Model):
    """スポンサードキャンペーン（その日の Quote を置き換える）"""
    name = models.CharField(max_length=200, help_text="内部管理用の名前")
    client_name = models.CharField(max_length=200, help_text="クライアント名（表示用）")
    text = models.TextField(help_text="キャンペーンテキスト（Quote の text 相当）")
    url = models.URLField(help_text="公式サイトURL")
    sns_url = models.URLField(blank=True, help_text="SNS URL（任意）")
    
    start_date = models.DateField(help_text="配信開始日")
    end_date = models.DateField(help_text="配信終了日")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "キャンペーン"
        verbose_name_plural = "キャンペーン"
    
    def __str__(self):
        return f"{self.name} ({self.start_date} ~ {self.end_date})"


class QuoteView(models.Model):
    """Quote の表示ログ"""
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='views')
    client_id = models.CharField(max_length=100, help_text="匿名ユーザーID")
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['quote', 'viewed_at']),
            models.Index(fields=['client_id', 'viewed_at']),
        ]
        verbose_name = "Quote 表示ログ"
        verbose_name_plural = "Quote 表示ログ"
    
    def __str__(self):
        return f"Quote#{self.quote_id} viewed at {self.viewed_at}"


class QuoteClick(models.Model):
    """Quote 内のアクション（Wiki/Amazon/Share）"""
    ACTION_CHOICES = [
        ('wiki', 'Wikipedia'),
        ('amazon', 'Amazon'),
        ('share', 'Share'),
    ]
    
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='clicks')
    client_id = models.CharField(max_length=100)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    clicked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-clicked_at']
        indexes = [
            models.Index(fields=['quote', 'action', 'clicked_at']),
            models.Index(fields=['client_id', 'clicked_at']),
        ]
        verbose_name = "Quote クリックログ"
        verbose_name_plural = "Quote クリックログ"
    
    def __str__(self):
        return f"Quote#{self.quote_id} {self.action} at {self.clicked_at}"


class CampaignView(models.Model):
    """Campaign の表示ログ"""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='views')
    client_id = models.CharField(max_length=100)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['campaign', 'viewed_at']),
            models.Index(fields=['client_id', 'viewed_at']),
        ]
        verbose_name = "Campaign 表示ログ"
        verbose_name_plural = "Campaign 表示ログ"
    
    def __str__(self):
        return f"Campaign#{self.campaign_id} viewed at {self.viewed_at}"


class CampaignClick(models.Model):
    """Campaign の CTA クリックログ"""
    ACTION_CHOICES = [
        ('official', '公式サイト'),
        ('sns', 'SNS'),
        ('share', 'Share'),
    ]
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='clicks')
    client_id = models.CharField(max_length=100)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='official')
    clicked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-clicked_at']
        indexes = [
            models.Index(fields=['campaign', 'action', 'clicked_at']),
            models.Index(fields=['client_id', 'clicked_at']),
        ]
        verbose_name = "Campaign クリックログ"
        verbose_name_plural = "Campaign クリックログ"
    
    def __str__(self):
        return f"Campaign#{self.campaign_id} {self.action} at {self.clicked_at}"
