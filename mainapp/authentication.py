from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class _TokenUser:
    """Minimal user-like object populated from JWT claims."""
    is_authenticated = True

    def __init__(self, claims: dict):
        self.claims = claims

    def get(self, key, default=None):
        return self.claims.get(key, default)

    def __getitem__(self, key):
        return self.claims[key]

    def __repr__(self):
        return f"<TokenUser generator_id={self.claims.get('generator_id')}>"


class GeneratorTokenAuthentication(BaseAuthentication):
    """
    Bearer JWT authentication for generator accounts and workers.

    Decodes the token, extracts custom claims, and sets request.user to
    a lightweight _TokenUser dict-like object. No Django User model lookup.

    Token claims injected at login:
        type         : 'account' | 'worker'
        generator_id : int — the owning generator's Account.id
        account_id   : int (accounts only)
        worker_id    : int (workers only)
        generator_name: str
    """

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None  # No credentials → allow AllowAny views

        token_str = auth_header[7:]  # strip "Bearer "
        try:
            token = UntypedToken(token_str)
        except (InvalidToken, TokenError) as exc:
            raise AuthenticationFailed(f'توكن غير صالح: {exc}')

        claims = {
            'type': token.get('type'),
            'generator_id': token.get('generator_id'),
            'account_id': token.get('account_id'),
            'worker_id': token.get('worker_id'),
            'generator_name': token.get('generator_name'),
        }

        if not claims['generator_id']:
            raise AuthenticationFailed('توكن لا يحتوي على معرف المولدة')

        user = _TokenUser(claims)
        return (user, claims)

    def authenticate_header(self, request):
        return 'Bearer'
