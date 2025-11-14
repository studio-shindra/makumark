# Generated manually for splitting author field

from django.db import migrations, models


def migrate_author_data(apps, schema_editor):
    """
    既存のauthorフィールドのデータをauthor_nameとsourceに分割
    authorが「作者名 / 出典」形式なら分割、そうでなければauthor_nameに全て入れる
    """
    Quote = apps.get_model('quotes', 'Quote')
    for quote in Quote.objects.all():
        if quote.author:
            # 「/」で分割を試みる
            if ' / ' in quote.author:
                parts = quote.author.split(' / ', 1)
                quote.author_name = parts[0].strip()
                quote.source = parts[1].strip() if len(parts) > 1 else ''
            elif '/' in quote.author:
                parts = quote.author.split('/', 1)
                quote.author_name = parts[0].strip()
                quote.source = parts[1].strip() if len(parts) > 1 else ''
            else:
                # 分割できない場合は全てauthor_nameに入れる
                quote.author_name = quote.author
                quote.source = ''
            quote.save()


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0001_initial'),
    ]

    operations = [
        # 新しいフィールドを追加
        migrations.AddField(
            model_name='quote',
            name='author_name',
            field=models.CharField(blank=True, help_text='例: シェイクスピア、太宰治', max_length=100, verbose_name='作者名'),
        ),
        migrations.AddField(
            model_name='quote',
            name='source',
            field=models.CharField(blank=True, help_text='例: ハムレット、人間失格', max_length=200, verbose_name='出典'),
        ),
        # 既存データを移行
        migrations.RunPython(migrate_author_data, migrations.RunPython.noop),
        # 古いauthorフィールドを削除
        migrations.RemoveField(
            model_name='quote',
            name='author',
        ),
    ]


