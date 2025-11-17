from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    拡張 User モデル。Apple Sign-In 対応、is_premium と premium_expires_at を追加。
    """
    apple_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Apple ID",
        help_text="Apple Sign-In で取得した user identifier",
    )
    is_premium = models.BooleanField(
        default=False,
        verbose_name="プレミアム購読中",
    )
    premium_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="プレミアム有効期限",
    )

    class Meta:
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー"

    def __str__(self) -> str:
        return self.username or self.apple_id or f"User {self.id}"


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
    original_text = models.TextField(
        blank=True,
        verbose_name="原文の台詞",
    )
    author_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="作者名",
        help_text="例: シェイクスピア、太宰治",
    )
    source = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="出典",
        help_text="例: ハムレット、人間失格",
    )
    original_source = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="原題",
        help_text="例: Hamlet, Cyrano de Bergerac",
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
    wiki_key = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Wiki検索キーワード",
        help_text="Wikipedia検索用キーワード。空ならリンク無し",
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
    User に紐づけて複数デバイスで同期。
    移行期間のため client_id も残す（後方互換）。
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="ユーザー",
        null=True,
        blank=True,
    )
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
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["client_id"]),
        ]

    def __str__(self) -> str:
        if self.user:
            return f"{self.user.username} ❤ {self.quote_id}"
        return f"{self.client_id} ❤ {self.quote_id}"