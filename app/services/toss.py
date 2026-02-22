import httpx
import base64
from app.config import settings

TOSS_API_URL = "https://api.tosspayments.com/v1"


def get_auth_header() -> dict:
    """인증 헤더 생성"""
    credentials = f"{settings.TOSS_SECRET_KEY}:"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json"
    }


async def confirm_payment(payment_key: str, order_id: str, amount: int) -> dict:
    """
    결제 승인
    https://docs.tosspayments.com/reference#결제-승인
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TOSS_API_URL}/payments/confirm",
            headers=get_auth_header(),
            json={
                "paymentKey": payment_key,
                "orderId": order_id,
                "amount": amount
            }
        )

        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.json()}


async def cancel_payment(payment_key: str, cancel_reason: str) -> dict:
    """
    결제 취소
    https://docs.tosspayments.com/reference#결제-취소
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TOSS_API_URL}/payments/{payment_key}/cancel",
            headers=get_auth_header(),
            json={"cancelReason": cancel_reason}
        )

        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.json()}


async def partial_cancel_payment(
    payment_key: str,
    cancel_reason: str,
    cancel_amount: int
) -> dict:
    """부분 취소"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TOSS_API_URL}/payments/{payment_key}/cancel",
            headers=get_auth_header(),
            json={
                "cancelReason": cancel_reason,
                "cancelAmount": cancel_amount
            }
        )

        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.json()}


async def get_payment(payment_key: str) -> dict:
    """결제 조회"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TOSS_API_URL}/payments/{payment_key}",
            headers=get_auth_header()
        )

        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.json()}
