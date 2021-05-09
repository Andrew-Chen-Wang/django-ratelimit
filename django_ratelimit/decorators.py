from __future__ import absolute_import

from functools import wraps

from django_ratelimit import ALL, UNSAFE
from django_ratelimit.exceptions import Ratelimited
from django_ratelimit.core import is_ratelimited


__all__ = ['ratelimit']


def ratelimit(group=None, key=None, rate=None, method=ALL, block=True, message=None):
    def decorator(view):
        @wraps(view)
        def _wrapped(request, *args, **kw):
            old_limited = getattr(request, "limited", False)
            usage = get_usage(
                request=request,
                group=group,
                fn=view,
                key=key,
                rate=rate,
                method=method,
                increment=True
            )
            if usage is None:
                usage = {
                    "should_limit": False,
                    "time_left": -1,
                }
            limited = usage["should_limit"]
            request.limited = limited or old_limited
            if limited and block:
                raise Ratelimited(detail=message, wait=usage["time_left"])
            return view(request, *args, **kw)
        return _wrapped
    return decorator


ratelimit.ALL = ALL
ratelimit.UNSAFE = UNSAFE
