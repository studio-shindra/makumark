from django.urls import path
from .views import TodayQuoteView, ToggleFavoriteView, FavoriteListView, QuoteByDateView

urlpatterns = [
    path("today/", TodayQuoteView.as_view(), name="today-quote"),
    path("by-date/", QuoteByDateView.as_view(), name="quote-by-date"),  # ← 追加
    path("<int:pk>/toggle-favorite/", ToggleFavoriteView.as_view(), name="toggle-favorite"),
    path("favorites/", FavoriteListView.as_view(), name="favorite-list"),
]