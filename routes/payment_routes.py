import json
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.auth_service import get_current_user
from app.env_reader import EnvReader
from app.logs_config import get_logger
from app.settings import (
    NOWPAYMENTS_API_BASE,
    NOWPAYMENTS_FEE_PAID_BY_USER,
    NOWPAYMENTS_PAYMENT_CURRENCY,
)
from app.utils import np_signature_check
from db_handles.admin_settings import AdminSettings
from db_handles.user import User
from models.payment import PaymentStatusUpdate

logger = get_logger()


payments_router = APIRouter(prefix="/payments", tags=["Payments"])


CREATE_INCOIVE = "/create-invoice"
PAYMENT_CONFIRMATION = "/confirmation"


@payments_router.post(CREATE_INCOIVE)
async def create_payment(user: User = Depends(get_current_user)) -> dict[str, Any]:
    """Create a new crypto payment"""
    if not EnvReader.NOWPAYMENTS_API_KEY:
        logger.debug("NOWPayments API key not set")
        raise HTTPException(status_code=500, detail="Internal server error")

    admin_settings = await AdminSettings.get_settings()
    if not admin_settings:
        raise HTTPException(
            403, "Payments are not enabled by admin yet! Please try again later!"
        )

    payload: dict[str, Any] = {
        "price_amount": 10,
        "price_currency": NOWPAYMENTS_PAYMENT_CURRENCY,
        "order_id": user.id,
        "order_description": f"Subscription for user {user.id}",
        "ipn_callback_url": f"https://{EnvReader.BACKEND_HOST}/payments/{PAYMENT_CONFIRMATION}",
        "success_url": f"https://{EnvReader.FRONTEND_HOST}/dashboard",
        "cancel_url": f"https://{EnvReader.FRONTEND_HOST}/dashboard",
        "is_fee_paid_by_user": NOWPAYMENTS_FEE_PAID_BY_USER,
    }
    logger.debug(f"Invoice creation payload for NowPayments: {payload}")
    headers: dict[str, Any] = {
        "x-api-key": EnvReader.NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json",
    }
    logger.debug(f"Headers for NowPayments API: {headers}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{NOWPAYMENTS_API_BASE}/invoice", json=payload, headers=headers
        )
        logger.debug(
            f"Invoice creation response from NowPayments: {response.text}, status code: {response.status_code}, reason: {response.reason_phrase}"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail="There was an error creating invoice. Please try again later!",
        )

    invoice_details = dict(response.json())

    # Remove the critical details from the invoice for security reasons
    invoice_details.pop("ipn_callback_url", "")
    invoice_details.pop("order_description", "")
    invoice_details.pop("order_id", "")
    invoice_details.pop("is_fee_paid_by_user", "")
    invoice_details.pop("customer_email", "")
    invoice_details.pop("token_id", "")
    invoice_details.pop("collect_user_data", "")
    invoice_details.pop("source", "")

    logger.debug(f"Final invoice to send out to user: {invoice_details}")

    return invoice_details


@payments_router.post(PAYMENT_CONFIRMATION)
async def handle_payment_webhook(
    request: Request, payload: PaymentStatusUpdate
) -> JSONResponse:
    """Receive payment status from NOWPayments and activate subscription"""
    logger.debug(f"Payment update received: {payload}")

    x_now_payments_sig = request.headers.get("x-nowpayments-sig", None)
    logger.debug(f"x-nowpayments-sig header: {x_now_payments_sig}")

    if not x_now_payments_sig:
        raise HTTPException(status_code=403, detail="Missing x-nowpayments-sig header")

    if not EnvReader.NOWPAYMENTS_IPN_KEY:
        raise HTTPException(status_code=403, detail="NOWPayments secret key not set")

    sorted_msg = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    np_signature_check(EnvReader.NOWPAYMENTS_IPN_KEY, x_now_payments_sig, sorted_msg)

    logger.debug("Signature check passed")

    if payload.payment_status.lower() == "finished":
        if not payload.order_id:
            logger.debug(f"Order ID was not found in the payload: {payload}")
            raise HTTPException(
                status_code=400, detail="Order ID not found in the payload"
            )

        user = await User.get_by_id(int(payload.order_id))

        if user:
            # Activate subscription
            logger.debug(f"Paying user found: {user}")
            logger.debug(f"Activating the subscription for user: {user.id}")
            logger.debug(f"User subscription updated: {user}")

        else:
            logger.error(f"Paying user was not found {payload.order_id}")

    return JSONResponse(status_code=200, content={"message": "Webhook received"})
