from django.urls import path, include
from rest_framework import routers
from .views import UserWalletViewSet


router = routers.DefaultRouter()
router.register('', UserWalletViewSet)

urlpatterns = [
    path('charge-wallet-send-otp/', UserWalletViewSet.as_view({'post': 'charge_wallet_send_otp'})),
    path('charge-wallet-confirmation/', UserWalletViewSet.as_view({'post': 'charge_wallet_confirmation'})),
    path('get-user-charge/', UserWalletViewSet.as_view({'get': 'get_user_charge'})),
    path('', include(router.urls)),
]