from rest_framework import serializers
from .models import Quote, User


class UserSerializer(serializers.ModelSerializer):
    """
    User モデルのシリアライザー。is_premium を含む。
    """
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "apple_id",
            "is_premium",
            "premium_expires_at",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "apple_id",
            "is_premium",
            "premium_expires_at",
        ]


class QuoteSerializer(serializers.ModelSerializer):
    liked = serializers.BooleanField(read_only=True)
    # frontend で使いやすいように、Amazonリンクを組み立てて渡してもOK
    
    # レスポンスをカスタマイズして、author_nameとsourceを確実に返す
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # author_nameとsourceが空の場合、tagsから作者名を取得
        if not data.get('author_name') and not data.get('source'):
            tags = data.get('tags', '')
            if tags:
                # tagsが「シェイクスピア」のような形式の場合、author_nameに設定
                tag_list = [t.strip() for t in tags.split(',')]
                if tag_list:
                    # 最初のタグをauthor_nameとして使用
                    data['author_name'] = tag_list[0]
        
        # データベースにauthor_nameとsourceが存在することを確認
        # 空文字列の場合はNoneにしない（フロントエンドで扱いやすくするため）
        if data.get('author_name') == '':
            data['author_name'] = None
        if data.get('source') == '':
            data['source'] = None
        
        return data

    class Meta:
        model = Quote
        fields = [
            "id",
            "text",
            "original_text",
            "author_name",
            "source",
            "original_source",
            "category",
            "tags",
            "publish_date",
            "is_public_domain",
            "amazon_key",
            "wiki_key",
            "bg_image_url",
            "like_count",
            "liked",
        ]