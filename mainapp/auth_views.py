from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from mainapp.models import Account, Worker


# ─── Token factories ────────────────────────────────────────────────────────

def _make_account_tokens(account: Account) -> dict:
    refresh = RefreshToken()
    refresh['type'] = 'account'
    refresh['account_id'] = account.id
    refresh['generator_id'] = account.id          # same as account_id for managers
    refresh['generator_name'] = account.generator_name
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'type': 'account',
        'generator_id': account.id,
        'generator_name': account.generator_name,
    }


def _make_worker_tokens(worker: Worker) -> dict:
    refresh = RefreshToken()
    refresh['type'] = 'worker'
    refresh['worker_id'] = worker.id
    refresh['generator_id'] = worker.generator_id
    refresh['generator_name'] = worker.generator.generator_name
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'type': 'worker',
        'worker_id': worker.id,
        'worker_name': worker.name,
        'generator_id': worker.generator_id,
        'generator_name': worker.generator.generator_name,
    }


# ─── Views ──────────────────────────────────────────────────────────────────

class AccountRegisterView(APIView):
    """
    Register a new generator account.
    POST { generator_name, phone, password }
    """
    def post(self, request):
        generator_name = request.data.get('generator_name', '').strip()
        phone          = request.data.get('phone', '').strip()
        password       = request.data.get('password', '').strip()

        if not generator_name or not phone or not password:
            return Response(
                {'detail': 'اسم المولدة ورقم الهاتف وكلمة المرور مطلوبة'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(password) < 4:
            return Response(
                {'detail': 'كلمة المرور يجب أن تكون 4 أحرف على الأقل'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Account.objects.filter(generator_name=generator_name).exists():
            return Response(
                {'detail': 'اسم المولدة مستخدم مسبقاً'},
                status=status.HTTP_409_CONFLICT,
            )
        if Account.objects.filter(phone=phone).exists():
            return Response(
                {'detail': 'رقم الهاتف مستخدم مسبقاً'},
                status=status.HTTP_409_CONFLICT,
            )

        account = Account(generator_name=generator_name, phone=phone)
        account.set_password(password)
        account.save()
        return Response(_make_account_tokens(account), status=status.HTTP_201_CREATED)


class AccountLoginView(APIView):
    """
    Login for generator account owners.
    POST { generator_name, password }
    Returns JWT access + refresh tokens.
    """
    def post(self, request):
        generator_name = request.data.get('generator_name', '').strip()
        password       = request.data.get('password', '').strip()

        if not generator_name or not password:
            return Response(
                {'detail': 'اسم المولدة وكلمة المرور مطلوبان'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            account = Account.objects.get(
                generator_name=generator_name, is_active=True
            )
        except Account.DoesNotExist:
            return Response(
                {'detail': 'اسم المولدة أو كلمة المرور غير صحيحة'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not account.check_credentials(password):
            return Response(
                {'detail': 'اسم المولدة أو كلمة المرور غير صحيحة'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(_make_account_tokens(account), status=status.HTTP_200_OK)


class WorkerLoginView(APIView):
    """
    Login for workers.
    POST { phone, password }
    Returns JWT access + refresh tokens.
    """
    def post(self, request):
        phone = request.data.get('phone', '').strip()
        password = request.data.get('password', '').strip()

        if not phone or not password:
            return Response(
                {'detail': 'رقم الهاتف وكلمة المرور مطلوبان'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            worker = Worker.objects.select_related(
                'generator'
            ).get(phone=phone, is_active=True)
        except Worker.DoesNotExist:
            return Response(
                {'detail': 'رقم الهاتف أو كلمة المرور غير صحيحة'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not worker.check_password(password):
            return Response(
                {'detail': 'رقم الهاتف أو كلمة المرور غير صحيحة'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(_make_worker_tokens(worker), status=status.HTTP_200_OK)


class TokenRefreshView(APIView):
    """
    Refresh an expired access token.
    POST { refresh }
    """
    def post(self, request):
        refresh_token = request.data.get('refresh', '').strip()
        if not refresh_token:
            return Response(
                {'detail': 'توكن التحديث مطلوب'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            return Response({'access': str(token.access_token)})
        except Exception:
            return Response(
                {'detail': 'توكن التحديث منتهي الصلاحية أو غير صالح'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
