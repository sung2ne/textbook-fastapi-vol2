import random
import string
from datetime import datetime


def generate_order_number() -> str:
    """
    주문번호 생성
    형식: YYYYMMDD-XXXXXX (예: 20240315-A3B2C1)
    """
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{date_part}-{random_part}"
