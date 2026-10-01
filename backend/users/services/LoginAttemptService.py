# external libraries imports
import hashlib

from django.core.cache import cache
from rest_framework.request import Request
from rest_framework.throttling import BaseThrottle


# main class
class LoginAttemptService:
    MAX_FAILURES_PER_EMAIL = 5
    # higher than per email: behind a NAT several people share one address
    MAX_FAILURES_PER_IP = 20
    LOCKOUT_SECONDS = 15 * 60

    @staticmethod
    def is_locked(request: Request, email: str) -> bool:
        email_key, ip_key = LoginAttemptService._keys(request, email)
        failures = cache.get_many([email_key, ip_key])

        return (
            failures.get(email_key, 0) >= LoginAttemptService.MAX_FAILURES_PER_EMAIL
            or failures.get(ip_key, 0) >= LoginAttemptService.MAX_FAILURES_PER_IP
        )

    @staticmethod
    def register_failure(request: Request, email: str) -> None:
        for key in LoginAttemptService._keys(request, email):
            cache.set(key, cache.get(key, 0) + 1, LoginAttemptService.LOCKOUT_SECONDS)

    # the IP counter is kept on purpose: anyone could reset it by logging in with their own account
    @staticmethod
    def register_success(request: Request, email: str) -> None:
        email_key, _ = LoginAttemptService._keys(request, email)
        cache.delete(email_key)

    # hashed so the cache table never stores an email or an address in clear text
    @staticmethod
    def _keys(request: Request, email: str) -> tuple[str, str]:
        ip = BaseThrottle().get_ident(request)

        return (
            f'login_failures:email:{LoginAttemptService._digest(email.strip().lower())}',
            f'login_failures:ip:{LoginAttemptService._digest(ip)}',
        )

    @staticmethod
    def _digest(value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()
