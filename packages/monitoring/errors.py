from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ErrorEvent:
    error_type: str
    message: str
    method: str
    path: str


class ErrorTracker(Protocol):
    def capture(self, request: Any, exc: BaseException) -> ErrorEvent:
        """Record an exception and return its normalized operational event."""


class LoggingErrorTracker:
    """Local error-tracking boundary backed by application logging."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger("advance_trading_system.errors")

    def capture(self, request: Any, exc: BaseException) -> ErrorEvent:
        event = ErrorEvent(
            error_type=type(exc).__name__,
            message=str(exc),
            method=getattr(request, "method", "UNKNOWN"),
            path=str(getattr(request, "url", "unknown")),
        )
        try:
            self._logger.exception(
                "unhandled_exception: %s",
                event.message,
                extra={
                    "error_type": event.error_type,
                    "error_message": event.message,
                    "request_method": event.method,
                    "request_path": event.path,
                },
            )
        except Exception:
            # Error tracking must never mask the original application failure.
            pass
        return event
