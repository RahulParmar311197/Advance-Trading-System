from __future__ import annotations

import logging

from packages.monitoring.errors import ErrorEvent, LoggingErrorTracker


class Request:
    method = "POST"
    url = "http://testserver/backtest"


def test_error_tracker_returns_normalized_event_and_logs_traceback(caplog) -> None:
    tracker = LoggingErrorTracker(logging.getLogger("test-errors"))
    exc = ValueError("bad request state")

    with caplog.at_level(logging.ERROR, logger="test-errors"):
        event = tracker.capture(Request(), exc)

    assert event == ErrorEvent(
        "ValueError",
        "bad request state",
        "POST",
        "http://testserver/backtest",
    )
    assert "unhandled_exception: bad request state" in caplog.text


def test_error_tracker_does_not_propagate_logger_failure() -> None:
    class BrokenLogger:
        def error(self, *_args, **_kwargs):
            raise RuntimeError("logger unavailable")

    tracker = LoggingErrorTracker(BrokenLogger())
    event = tracker.capture(Request(), RuntimeError("original"))

    assert event.error_type == "RuntimeError"
    assert event.message == "original"
