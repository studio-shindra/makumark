from rest_framework import serializers
from .models import Quote


class QuoteSerializer(serializers.ModelSerializer):
    liked = serializers.BooleanField(read_only=True)
    # frontend で使いやすいように、Amazonリンクを組み立てて渡してもOK

    class Meta:
        model = Quote
        fields = [
            "id",
            "text",
            "author",
            "category",
            "tags",
            "publish_date",
            "is_public_domain",
            "bg_image_url",
            "like_count",
            "liked",
        ]