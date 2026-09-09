from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .schemas import RawOHLCV


class ImmutableRawStorage:
    """Content-addressed local storage for provider-sourced raw OHLCV."""

    def __init__(self, root: str | Path = "data/raw") -> None:
        self.root = Path(root)

    def write_ohlcv(self, rows: Iterable[RawOHLCV]) -> str:
        payload = [asdict(row) for row in rows]
        canonical = json.dumps(payload, default=str, sort_keys=True, separators=(",", ":")).encode()
        version = hashlib.sha256(canonical).hexdigest()
        target = self.root / f"ohlcv-{version}.json"
        self.root.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(canonical)
        return version

    def read(self, version: str) -> bytes:
        if not version or "/" in version or "\\" in version or ".." in version:
            raise ValueError("invalid data version")
        return (self.root / f"ohlcv-{version}.json").read_bytes()
