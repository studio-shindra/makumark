from django.db import models


class Quote(models.Model):
    CATEGORY_CHOICES = [
        ("classic", "Classic"),
        ("drama", "Drama"),
        ("comedy", "Comedy"),
        ("love", "Love"),
        ("horror", "Horror"),
        ("other", "Other"),
    ]

    text = models.TextField(verbose_name="台詞本文")
    author = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="作者名・出典",
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="other",
        verbose_name="カテゴリ",
    )
    tags = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="タグ（カンマ区切り）",
        help_text="例: 愛, 家族, 雨",
    )
    publish_date = models.DateField(
        verbose_name="配信日（今日の1本になる日）",
        help_text="この日付の quote が『今日の1本』として扱われる",
        db_index=True,
    )
    is_public_domain = models.BooleanField(
        default=False,
        verbose_name="著作権切れ（公有）か？",
    )
    amazon_key = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Amazonキー（ASIN or 検索キーワード）",
        help_text="ASIN or 検索用キーワード。空ならリンク無し",
    )
    bg_image_url = models.URLField(
        blank=True,
        verbose_name="背景画像URL（Cloudinary など）",
    )
    like_count = models.PositiveIntegerField(
        default=0,
        verbose_name="いいね数",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        ordering = ["-publish_date", "-id"]

    def __str__(self) -> str:
        return f"{self.publish_date}: {self.text[:30]}"


class Favorite(models.Model):
    """
    いいね情報。
    ログインユーザーではなく「クライアントID（端末 or アプリ内UUID）」で紐づける。
    frontend 側でランダムに UUID を作り、ずっと使い回す想定。
    """

    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="台詞",
    )
    client_id = models.CharField(
        max_length=64,
        verbose_name="クライアントID（端末UUIDなど）",
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        unique_together = ("quote", "client_id")
        indexes = [
            models.Index(fields=["client_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.client_id} ❤ {self.quote_id}"