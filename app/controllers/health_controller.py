from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
import time

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check(db: Session = Depends(get_db)):
    start = time.time()

    # Перевірка підключення до БД
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    response_time_ms = round((time.time() - start) * 1000, 2)

    overall = "ok" if db_status == "ok" else "degraded"

    return {
        "status": overall,
        "services": {
            "api": "ok",
            "database": db_status,
        },
        "response_time_ms": response_time_ms,
    }
