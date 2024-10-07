from rest_framework import serializers
from .models import UserWallet

    
class ChargeWalletRequest(serializers.Serializer):
    amount = serializers.IntegerField(required=True)
    
class ChargeWalletResponse(serializers.ModelSerializer):
    class Meta:
        model = UserWallet
        fields = "__all__"
        depth = 0
    
class SendOTPRequest(serializers.Serializer):
    phone_number = serializers.CharField(required=True)