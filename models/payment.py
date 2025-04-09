"""nowpayments.io related models"""

from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel


class PaymentRequest(BaseModel):
    price_amount: float
    price_currency: str  # e.g. "usd"
    pay_currency: str  # e.g. "btc"
    order_id: str  # user_id or UUID4
    order_description: str
    ipn_callback_url: str


class Fee(BaseModel):
    currency: str
    depositFee: float
    withdrawalFee: float
    serviceFee: float


class PaymentStatusUpdate(BaseModel):
    payment_id: int
    parent_payment_id: int
    invoice_id: Optional[str] = None
    payment_status: str
    pay_address: str
    payin_extra_id: Optional[str] = None
    price_amount: float
    price_currency: str
    pay_amount: float
    actually_paid: float
    actually_paid_at_fiat: float
    pay_currency: str
    order_id: Optional[str] = None
    order_description: Optional[str] = None
    purchase_id: str
    outcome_amount: float
    outcome_currency: str
    payment_extra_ids: Optional[str] = None
    fee: Fee
