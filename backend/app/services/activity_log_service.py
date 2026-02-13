import json
import logging
from typing import Any, Optional

from app.database import SessionLocal
from app.models import ActivityLog, User

logger = logging.getLogger(__name__)


class ActivityLogService:
    def safe_log(
        self,
        *,
        action: str,
        user: Optional[User] = None,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        method: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        duration_ms: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Any] = None,
    ) -> None:
        resolved_user_id = user.id if user else user_id
        resolved_user_email = user.email if user else user_email
        serialized_details = self._serialize_details(details)

        db = SessionLocal()
        try:
            log_row = ActivityLog(
                action=action,
                user_id=resolved_user_id,
                user_email=resolved_user_email,
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration_ms=duration_ms,
                ip_address=ip_address,
                user_agent=(user_agent or "")[:255] or None,
                details=serialized_details,
            )
            db.add(log_row)
            db.commit()
        except Exception as exc:
            db.rollback()
            logger.warning("Failed to write activity log: %s", exc)
        finally:
            db.close()

    @staticmethod
    def _serialize_details(details: Optional[Any]) -> Optional[str]:
        if details is None:
            return None
        if isinstance(details, str):
            return details[:4000]
        try:
            return json.dumps(details, ensure_ascii=False, default=str)[:4000]
        except Exception:
            return str(details)[:4000]


activity_log_service = ActivityLogService()
