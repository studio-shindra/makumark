from datetime import date

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from .models import Quote, Favorite, User
from .serializers import QuoteSerializer, UserSerializer

from django.db import models, transaction
import json
import logging

logger = logging.getLogger(__name__)

def get_client_id_from_request(request):
    """
    端末側で発行した client_id（UUIDなど）をヘッダー or クエリ or ボディから拾う。
    まずはシンプルにクエリ or ヘッダーを使う。
    """
    cid = request.headers.get("X-Client-Id") or request.query_params.get("client_id")
    return cid or ""


class AppleSignInView(APIView):
    """
    Apple Sign-In の結果を受け取り、User を作成または取得:
    POST /api/auth/signin/
    body: { "apple_id": "001234.xxx", "id_token": "eyJxxx...", "email": "user@example.com" }
    """
    permission_classes = []  # 認証不要

    def post(self, request, format=None):
        apple_id = request.data.get("apple_id")
        id_token = request.data.get("id_token")
        email = request.data.get("email")

        if not apple_id:
            return Response({"detail": "apple_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # TODO: id_token を Apple に検証（本番環境では必須）
        # https://developer.apple.com/documentation/sign_in_with_apple/sign_in_with_apple_rest_api/verifying_a_user
        
        try:
            # User を取得または作成
            user, created = User.objects.get_or_create(
                apple_id=apple_id,
                defaults={
                    "username": apple_id,
                    "email": email or "",
                }
            )
            
            # Token を取得または作成
            token, _ = Token.objects.get_or_create(user=user)
            
            serializer = UserSerializer(user)
            
            logger.info(f"User {'created' if created else 'retrieved'}: {user.id} (Apple ID: {apple_id})")
            
            return Response({
                "token": token.key,
                "user": serializer.data,
                "created": created,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Apple Sign-In error: {str(e)}")
            return Response(
                {"detail": "Sign-in failed"},
                status=status.HTTP_400_BAD_REQUEST
            )


class MeView(APIView):
    """
    現在のユーザー情報を返す:
    GET /api/me/
    """

    def get(self, request, format=None):
        if not request.user.is_authenticated:
            return Response({"detail": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class SubscriptionVerifyView(APIView):
    """
    Apple receipt を検証して is_premium を設定する:
    POST /api/subscription/verify/
    body: { "receipt": "Base64EncodedReceiptData" }
    """

    def post(self, request, format=None):
        if not request.user.is_authenticated:
            return Response({"detail": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        receipt = request.data.get("receipt")
        if not receipt:
            return Response({"detail": "receipt is required"}, status=status.HTTP_400_BAD_REQUEST)

        # TODO: Apple verifyReceipt API に送信
        # https://developer.apple.com/documentation/appstoreconnectapi/app_store_server_api
        # または https://buy.itunes.apple.com/verifyReceipt (Sandbox)
        # 
        # ここでは簡略的に receipt の存在を確認して is_premium = True とする
        # 本番環境では必ず Apple に検証する必要がある
        
        try:
            # Apple verification (placeholder - implement with actual Apple API)
            # For now, just mark as premium if receipt is provided
            is_valid = len(receipt) > 0  # Placeholder validation
            
            if is_valid:
                user = request.user
                user.is_premium = True
                # 購読期間は1年とする（実装時は Apple の response から取得）
                from datetime import datetime, timedelta
                user.premium_expires_at = timezone.now() + timedelta(days=365)
                user.save()
                
                logger.info(f"User {user.id} marked as premium")
                
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "Invalid receipt"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Subscription verify error: {str(e)}")
            return Response(
                {"detail": "Verification failed"},
                status=status.HTTP_400_BAD_REQUEST
            )


class TodayQuoteView(APIView):
    """
    今日の1本を返すエンドポイント:
    GET /api/quotes/today?client_id=xxxx
    または GET /api/quotes/today/ (認証済み)
    
    ※ Campaign がある日は Campaign を Quote として返す
    """
    permission_classes = []  # 認証不要

    def get(self, request, format=None):
        from tracking.models import Campaign
        
        client_id = get_client_id_from_request(request)
        today = timezone.localdate()

        # Campaign チェック（今日が範囲内か）
        campaign = Campaign.objects.filter(
            start_date__lte=today,
            end_date__gte=today
        ).first()
        
        if campaign:
            # Campaign を Quote として返す
            liked = False
            if request.user.is_authenticated:
                liked = Favorite.objects.filter(campaign_id=campaign.id, user=request.user).exists()
            elif client_id:
                liked = Favorite.objects.filter(campaign_id=campaign.id, client_id=client_id).exists()
            
            return Response({
                "id": None,
                "campaign_id": campaign.id,
                "text": campaign.text,
                "client_name": campaign.client_name,
                "url": campaign.url,
                "sns_url": campaign.sns_url,
                "is_campaign": True,
                "liked": liked,
                "like_count": Favorite.objects.filter(campaign_id=campaign.id).count(),
            })

        # 通常の Quote
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

        # liked 判定: user 優先、なければ client_id
        liked = False
        if request.user.is_authenticated:
            liked = Favorite.objects.filter(quote=quote, user=request.user).exists()
        elif client_id:
            liked = Favorite.objects.filter(quote=quote, client_id=client_id).exists()

        serializer = QuoteSerializer(quote, context={"request": request})
        data = serializer.data
        data["liked"] = liked
        data["is_campaign"] = False

        return Response(data)


class ToggleFavoriteView(APIView):
    """
    いいねON/OFF切り替え:
    POST /api/quotes/<id>/toggle-favorite/
    または POST /api/campaigns/<id>/toggle-favorite/ (campaign_id を指定)
    認証済み → user に紐づけ
    未認証 → client_id に紐づけ（後方互換）
    """
    permission_classes = []  # 認証不要

    def post(self, request, pk, format=None):
        # Campaign のお気に入りか確認
        is_campaign = request.data.get('is_campaign', False)
        
        if is_campaign:
            # Campaign のお気に入り
            campaign_id = pk
            
            with transaction.atomic():
                # 認証済みユーザーの場合
                if request.user.is_authenticated:
                    fav, created = Favorite.objects.get_or_create(
                        campaign_id=campaign_id,
                        user=request.user,
                        defaults={'quote': None}
                    )
                    liked = created
                    if not created:
                        fav.delete()
                        liked = False
                        
                # 未認証の場合（client_id を使用）
                else:
                    client_id = (
                        request.data.get("client_id")
                        or request.headers.get("X-Client-Id")
                        or request.query_params.get("client_id")
                    )
                    if not client_id:
                        return Response({"detail": "client_id or authentication required"}, status=status.HTTP_400_BAD_REQUEST)

                    fav, created = Favorite.objects.get_or_create(
                        campaign_id=campaign_id,
                        client_id=client_id,
                        user=None,
                        defaults={'quote': None}
                    )
                    liked = created
                    if not created:
                        fav.delete()
                        liked = False

                like_count = Favorite.objects.filter(campaign_id=campaign_id).count()

            return Response({"liked": liked, "like_count": like_count})
        
        # Quote のお気に入り（既存ロジック）
        try:
            quote = Quote.objects.get(pk=pk)
        except Quote.DoesNotExist:
            return Response({"detail": "Quote not found"}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            # 認証済みユーザーの場合
            if request.user.is_authenticated:
                fav, created = Favorite.objects.get_or_create(
                    quote=quote,
                    user=request.user,
                )
                if created:
                    Quote.objects.filter(pk=quote.pk).update(like_count=models.F("like_count") + 1)
                    liked = True
                else:
                    fav.delete()
                    Quote.objects.filter(pk=quote.pk).update(like_count=models.F("like_count") - 1)
                    liked = False
                    
            # 未認証の場合（client_id を使用）
            else:
                client_id = (
                    request.data.get("client_id")
                    or request.headers.get("X-Client-Id")
                    or request.query_params.get("client_id")
                )
                if not client_id:
                    return Response({"detail": "client_id or authentication required"}, status=status.HTTP_400_BAD_REQUEST)

                fav, created = Favorite.objects.get_or_create(
                    quote=quote,
                    client_id=client_id,
                    user=None,
                )
                if created:
                    Quote.objects.filter(pk=quote.pk).update(like_count=models.F("like_count") + 1)
                    liked = True
                else:
                    fav.delete()
                    Quote.objects.filter(pk=quote.pk).update(like_count=models.F("like_count") - 1)
                    liked = False

            # 最新の like_count を再取得
            quote.refresh_from_db(fields=["like_count"])

        return Response({"liked": liked, "like_count": quote.like_count})


class FavoriteListView(APIView):
    """
    いいねした台詞一覧:
    GET /api/quotes/favorites?client_id=xxxx (未認証)
    または GET /api/quotes/favorites/ (認証済み)
    → MakuMark 内の「いいね一覧」画面で使う
    """
    permission_classes = []  # 認証不要

    def get(self, request, format=None):
        # 認証済みユーザーの場合
        if request.user.is_authenticated:
            favorites = Favorite.objects.filter(user=request.user).select_related("quote").order_by("-created_at")
        # 未認証の場合（client_id を使用）
        else:
            client_id = get_client_id_from_request(request)
            if not client_id:
                return Response({"detail": "client_id or authentication required"}, status=status.HTTP_400_BAD_REQUEST)
            favorites = Favorite.objects.filter(client_id=client_id, user=None).select_related("quote").order_by("-created_at")

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
    または GET /api/quotes/by-date/?date=YYYY-MM-DD (認証済み)
    
    ※ Campaign がある日は Campaign を Quote として返す
    """
    permission_classes = []  # 認証不要

    def get(self, request, format=None):
        from tracking.models import Campaign
        
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"detail": "date is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            return Response({"detail": "invalid date"}, status=status.HTTP_400_BAD_REQUEST)

        # Campaign チェック
        campaign = Campaign.objects.filter(
            start_date__lte=target_date,
            end_date__gte=target_date
        ).first()
        
        if campaign:
            # Campaign を Quote として返す
            client_id = get_client_id_from_request(request)
            liked = False
            if request.user.is_authenticated:
                liked = Favorite.objects.filter(campaign_id=campaign.id, user=request.user).exists()
            elif client_id:
                liked = Favorite.objects.filter(campaign_id=campaign.id, client_id=client_id).exists()
            
            return Response({
                "id": None,
                "campaign_id": campaign.id,
                "text": campaign.text,
                "client_name": campaign.client_name,
                "url": campaign.url,
                "sns_url": campaign.sns_url,
                "is_campaign": True,
                "liked": liked,
                "like_count": Favorite.objects.filter(campaign_id=campaign.id).count(),
            })

        # 通常の Quote
        try:
            quote = Quote.objects.get(publish_date=target_date)
        except Quote.DoesNotExist:
            return Response({"detail": "Quote not found"}, status=status.HTTP_404_NOT_FOUND)

        # liked 判定: user 優先、なければ client_id
        liked = False
        client_id = get_client_id_from_request(request)
        if request.user.is_authenticated:
            liked = Favorite.objects.filter(quote=quote, user=request.user).exists()
        elif client_id:
            liked = Favorite.objects.filter(quote=quote, client_id=client_id, user=None).exists()

        serializer = QuoteSerializer(quote, context={"request": request})
        data = serializer.data
        data["liked"] = liked
        data["is_campaign"] = False
        return Response(data)