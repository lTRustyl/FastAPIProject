from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from datetime import datetime

router = APIRouter(prefix="/health", tags=["Health"])

@router.get(
    "",
    summary="Health check",
    description="""
Returns the current health status of the service and its dependencies.

- `status: "ok"` — all systems operational
- `status: "degraded"` — API is running but database is unavailable

This endpoint does **not** require authentication and is intended for monitoring tools.
    """,
    responses={
        200: {
            "description": "Service health status",
            "content": {
                "application/json": {
                    "examples": {
                        "healthy": {
                            "summary": "All systems operational",
                            "value": {
                                "status": "ok",
                                "timestamp": "2024-01-10T12:00:00.000000",
                                "services": {"api": "ok", "database": "ok"},
                            },
                        },
                        "degraded": {
                            "summary": "Database unavailable",
                            "value": {
                                "status": "degraded",
                                "timestamp": "2024-01-10T12:00:00.000000",
                                "services": {
                                    "api": "ok",
                                    "database": "error: could not connect to server",
                                },
                            },
                        },
                    }
                }
            },
        }
    },
)
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "ok",
            "database": db_status,
        },
    }
