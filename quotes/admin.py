from django.contrib import admin
from .models import Quote, Favorite


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("publish_date", "short_text", "author", "category", "like_count", "is_public_domain")
    list_filter = ("category", "is_public_domain", "publish_date")
    search_fields = ("text", "author", "tags")
    date_hierarchy = "publish_date"
    ordering = ("-publish_date",)

    def short_text(self, obj):
        return (obj.text[:40] + "…") if len(obj.text) > 40 else obj.text

    short_text.short_description = "本文プレビュー"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("quote", "client_id", "created_at")
    list_filter = ("created_at",)
    search_fields = ("client_id",)