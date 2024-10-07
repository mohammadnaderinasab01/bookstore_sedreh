from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .serializer import ChargeWalletRequest, ChargeWalletResponse, SendOTPRequest
from rest_framework.parsers import MultiPartParser, JSONParser
from drf_spectacular.utils import extend_schema
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from authentication.authentication import UserAuthentication
from users.models import UserWallet
from sms_ir import SmsIr
import random, os
from datetime import datetime


sms_ir = SmsIr(
    api_key=os.getenv('SMS_API_KEY'),
    linenumber=os.getenv('SMS_LINE_NUMBER'),
)

user_authentication = UserAuthentication

class UserWalletViewSet(GenericViewSet):
    queryset = UserWallet.objects.all()
    parser_classes = (MultiPartParser, JSONParser)
    
    
    def dispatch(self, request, *args, **kwargs):
        if self.request.path == '/users/get-user-charge/' or self.request.path == '/users/charge-wallet-confirmation/' or self.request.path == '/users/charge-wallet-send-otp/':
            self.args = args
            self.kwargs = kwargs
            request = self.initialize_request(request, *args, **kwargs)
            self.request = request
            self.headers = self.default_response_headers
            self.authentication_classes = [UserAuthentication]

            response_exc = ''
            try:
                self.initial(request, *args, **kwargs)

                # Get the appropriate handler method
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(),
                                    self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed

                response = handler(request, *args, **kwargs)

            except Exception as exc:
                response_exc = exc
                response = self.handle_exception(exc)

            self.response = self.finalize_response(request, response, *args, **kwargs)
            if str(response_exc) == 'Invalid Token':
                self.response.status_code = 401
            return self.response
        self.authentication_classes = []
        return super().dispatch(request, *args, **kwargs)
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        else:
            return [IsAuthenticated(), IsAdminUser()]
        

    @extend_schema(
        request=SendOTPRequest
    )
    def charge_wallet_send_otp(self, request):
        if request.data.get('phone_number') == None:
            return Response({
                'validationMessage': [{
                    'statusCode': 400,
                    'message': 'شماره تلفن خود را وارد نمایید'
                }],
                'result': None,
                'resultStatus': 1
            }, status=400)
        random_code = random.randint(10000, 99999)
        cache.set(request.data.get('phone_number'), random_code, 120)
        sms = sms_ir.send_verify_code(
            number=f"+{request.data.get('phone_number')}",
            template_id=418701,
            parameters=[
                {
                    "name" : "code",
                    "value": str(random_code)
                },
            ],
        )
        return Response({
            'validationMessage': [{
                'statusCode': 200,
                'message': 'کد با موفقیت به شماره تلفن شما ارسال شد'
            }],
            'result': {
                'code_generation_datetime': datetime.now(),
                'code': str(random_code)
            },
            'resultStatus': 1
        }, status=200)
     
       
    @extend_schema(
        request=ChargeWalletRequest
    )
    def charge_wallet_confirmation(self, request):
        try:
            # /////////////////////////////////////////////////////////////////////
            # /////////////////////////////////////////////////////////////////////
            # /////////////////////////////////////////////////////////////////////
            # do something to validate the OTP code
            # /////////////////////////////////////////////////////////////////////
            # /////////////////////////////////////////////////////////////////////
            # /////////////////////////////////////////////////////////////////////
            
            
            if request.data.get('amount') == None:
                return Response({
                    'validationMessage': [{
                        'statusCode': 400,
                        'message': 'مبلغ درخواستی خود را وارد نمایید'
                    }],
                    'result': None,
                    'resultStatus': 1
                }, status=400)
            else:
                if int(request.data.get('amount')) < 0:
                    return Response({
                        'validationMessage': [{
                            'statusCode': 400,
                            'message': 'مبلغ درخواستی معتبر وارد نمایید'
                        }],
                        'result': None,
                        'resultStatus': 1
                    }, status=400)
                    
                user_wallet = UserWallet.objects.get(user__id=request.user.id)
                user_wallet.charge = UserWallet.objects.get(user__id=request.user.id).charge + int(request.data.get('amount'))
                user_wallet.save()
                user_wallet_response = ChargeWalletResponse(user_wallet, many=False)
                return Response({
                    'validationMessage': [{
                        'statusCode': 200,
                        'message': 'اطلاعات با موفقیت دریافت شد'
                    }],
                    'result': user_wallet_response.data,
                    'resultStatus': 0
                }, status=200)
        except Exception as e:
                return Response({
                    'validationMessage': [{
                        'statusCode': 500,
                        'message': 'درخواست شما با مشکل مواجه شد'
                    }],
                    'result': None,
                    'resultStatus': 1
                }, status=500)
            

    def get_user_charge(self, request):
        try:
            return Response({
                'validationMessage': [{
                    'statusCode': 200,
                    'message': 'اطلاعات با موفقیت دریافت شد'
                }],
                'result': UserWallet.objects.get(user__id=request.user.id).charge,
                'resultStatus': 0
            }, status=200)
        except Exception as e:
            print(e)
            print(type(e))
            return Response({
                'validationMessage': [{
                    'statusCode': 500,
                    'message': 'دریافت اطلاعات با خطا مواجه شد'
                }],
                'result': None,
                'resultStatus': 1
            }, status=500)