from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Quote, Favorite


class QuoteResource(resources.ModelResource):
    """CSV import/export用のリソース定義"""
    
    class Meta:
        model = Quote
        fields = (
            'id',
            'text',
            'original_text',
            'author_name',
            'source',
            'original_source',
            'category',
            'tags',
            'publish_date',
            'is_public_domain',
            'amazon_key',
            'wiki_key',
            'bg_image_url',
            'like_count',
        )
        export_order = (
            'id',
            'text',
            'original_text',
            'author_name',
            'source',
            'original_source',
            'category',
            'tags',
            'publish_date',
            'is_public_domain',
            'amazon_key',
            'wiki_key',
            'bg_image_url',
            'like_count',
        )
        import_id_fields = ['id']  # idで既存レコードを識別（新規作成時は空欄可）


@admin.register(Quote)
class QuoteAdmin(ImportExportModelAdmin):
    resource_class = QuoteResource
    list_display = ("publish_date", "short_text", "author_name", "source", "category", "like_count", "is_public_domain")
    list_filter = ("category", "is_public_domain", "publish_date")
    search_fields = ("text", "author_name", "source", "tags")
    date_hierarchy = "publish_date"
    ordering = ("-publish_date",)
    
    # CSV import/exportの設定
    import_export_change_list_template = "admin/import_export/change_list_import_export.html"

    def short_text(self, obj):
        return (obj.text[:40] + "…") if len(obj.text) > 40 else obj.text

    short_text.short_description = "本文プレビュー"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("quote", "client_id", "created_at")
    list_filter = ("created_at",)
    search_fields = ("client_id",)