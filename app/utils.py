import datetime as dt
import hmac
import hashlib
from fastapi import HTTPException


def dt_now() -> dt.datetime:
    return dt.datetime.now(tz=dt.timezone.utc)


def ts_now() -> int:
    return int(dt_now().timestamp())


def np_signature_check(
    np_secret_key: str, np_x_signature: str, sorted_msg: str
) -> bool:
    """Check the nowpayments.io payment status update signature"""
    # source: https://documenter.getpostman.com/view/7907941/2s93JusNJt
    digest = hmac.new(
        str(np_secret_key).encode(), f"{sorted_msg}".encode(), hashlib.sha512
    )
    signature = digest.hexdigest()

    if signature == np_x_signature:
        return True

    else:
        raise HTTPException(400, "HMAC signature does not match")
