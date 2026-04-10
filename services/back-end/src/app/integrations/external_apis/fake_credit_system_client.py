from __future__ import annotations

from app.domain_models.agent.models import CreditStatus
from app.domain_models.common.ids import SessionId


class FakeCreditSystemClient:
    def verify_credit(self, session_id: SessionId) -> CreditStatus:
        return CreditStatus(account_name=str(session_id), available=True)
