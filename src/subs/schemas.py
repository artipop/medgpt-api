from datetime import datetime
from enum import EnumType, StrEnum
from uuid import UUID

from pydantic import BaseModel


class SubscriptionPeriod(StrEnum):
    YEARLY = "YEARLY"
    MONTHLY = "MONTHLY"


class CreateSubscriptionData(BaseModel):
    # id: UUID
    period: SubscriptionPeriod  # MONTH or YEAR
    country_code: str


class SubscriptionData(BaseModel):
    id: UUID
    status: str
    expiration_date: datetime
    provider: str | None = None
