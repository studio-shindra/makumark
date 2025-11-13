from datetime import date

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Quote, Favorite
from .serializers import QuoteSerializer

from django.db import models, transaction

def get_client_id_from_request(request):
    """
    端末側で発行した client_id（UUIDなど）をヘッダー or クエリ or ボディから拾う。
    まずはシンプルにクエリ or ヘッダーを使う。
    """
    cid = request.headers.get("X-Client-Id") or request.query_params.get("client_id")
    return cid or ""


class TodayQuoteView(APIView):
    """
    今日の1本を返すエンドポイント:
    GET /api/quotes/today?client_id=xxxx
    """

    def get(self, request, format=None):
        client_id = get_client_id_from_request(request)
        today = timezone.localdate()

        # 今日の日付の quote があればそれを返す
        try:
            quote = Quote.objects.get(publish_date=today)
        except Quote.DoesNotExist:
            # なければ一番近い過去 or ランダム
            quote = (
                Quote.objects.filter(publish_date__lte=today).order_by("-publish_date").first()
                or Quote.objects.order_by("?").first()
            )
            if not quote:
                return Response({"detail": "No quotes available"}, status=status.HTTP_404_NOT_FOUND)

        liked = False
        if client_id:
            liked = Favorite.objects.filter(quote=quote, client_id=client_id).exists()

        serializer = QuoteSerializer(quote, context={"request": request})
        data = serializer.data
        data["liked"] = liked

        return Response(data)


class ToggleFavoriteView(APIView):
    """
    いいねON/OFF切り替え:
    POST /api/quotes/<id>/toggle-favorite/
    body: { "client_id": "xxxx" } でもOK
    """

    def post(self, request, pk, format=None):
        client_id = (
            request.data.get("client_id")
            or request.headers.get("X-Client-Id")
            or request.query_params.get("client_id")
        )
        if not client_id:
            return Response({"detail": "client_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quote = Quote.objects.get(pk=pk)
        except Quote.DoesNotExist:
            return Response({"detail": "Quote not found"}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            fav, created = Favorite.objects.get_or_create(
                quote=quote,
                client_id=client_id,
            )
            if created:
                # 追加 → いいね +1
                Quote.objects.filter(pk=quote.pk).update(like_count=models.F("like_count") + 1)  # type: ignore
                liked = True
            else:
                # すでにあれば解除
                fav.delete()
                Quote.objects.filter(pk=quote.pk).update(like_count=models.F("like_count") - 1)  # type: ignore
                liked = False

            # 最新の like_count を再取得
            quote.refresh_from_db(fields=["like_count"])

        return Response({"liked": liked, "like_count": quote.like_count})


class FavoriteListView(APIView):
    """
    いいねした台詞一覧:
    GET /api/quotes/favorites?client_id=xxxx
    → MakuMark 内の「いいね一覧」画面で使う
    （広告表示するか、サブスクで解放するかは frontend 側の制御）
    """

    def get(self, request, format=None):
        client_id = get_client_id_from_request(request)
        if not client_id:
            return Response({"detail": "client_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        favorites = Favorite.objects.filter(client_id=client_id).select_related("quote").order_by("-created_at")
        quotes = [f.quote for f in favorites]

        # 各 quote ごとの liked フラグは true 固定（自分が押した一覧なので）
        data = []
        for q in quotes:
            s = QuoteSerializer(q, context={"request": request}).data
            s["liked"] = True
            data.append(s)

        return Response(data)

    
class QuoteByDateView(APIView):
    """
    指定日付の台詞を返す:
    GET /api/quotes/by-date/?date=YYYY-MM-DD&client_id=xxxx
    """

    def get(self, request, format=None):
        client_id = get_client_id_from_request(request)
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"detail": "date is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            return Response({"detail": "invalid date"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quote = Quote.objects.get(publish_date=target_date)
        except Quote.DoesNotExist:
            return Response({"detail": "Quote not found"}, status=status.HTTP_404_NOT_FOUND)

        liked = False
        if client_id:
            liked = Favorite.objects.filter(quote=quote, client_id=client_id).exists()

        serializer = QuoteSerializer(quote, context={"request": request})
        data = serializer.data
        data["liked"] = liked
        return Response(data)