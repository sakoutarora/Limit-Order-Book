# persistence/wal.py
import os
import json
import asyncio
from typing import Dict, Any
from functools import wraps
from typing import Dict, Any, Callable, Coroutine


class WAL:
    """
    Append-only newline-delimited JSON WAL.
    Each record: {"seq": int, "op": "submit"|"modify"|"cancel", "data": {...}}
    """
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        self._lock = asyncio.Lock()
        # ensure WAL file exists
        open(self.path, "a", encoding="utf-8").close()
        # highest written seq
        self._last_seq = 0
        self._load_last_seq()

    def _load_last_seq(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        rec = json.loads(line)
                        seq = rec.get("seq", 0)
                        if seq > self._last_seq:
                            self._last_seq = seq
                    except Exception:
                        continue
        except FileNotFoundError:
            self._last_seq = 0

    async def append(self, op: str, data: Dict[str, Any]) -> int:
        """
        Append a WAL entry and fsync. Returns seq number.
        """
        async with self._lock:
            self._last_seq += 1
            record = {"seq": self._last_seq, "op": op, "data": data}
            line = json.dumps(record, separators=(",", ":")) + "\n"
            # append and fsync
            with open(self.path, "ab") as f:  # binary mode to fsync reliably
                f.write(line.encode("utf-8"))
                f.flush()
                os.fsync(f.fileno())
            return self._last_seq

    async def read_from(self, seq_exclusive: int = 0):
        """
        Yield records with seq > seq_exclusive
        """
        # Not locked: reading while writer appends is fine (we read full lines)
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                    if rec.get("seq", 0) > seq_exclusive:
                        yield rec
                except json.JSONDecodeError:
                    # skip a corrupted line or partial write (shouldn't happen if fsync)
                    continue

    async def truncate(self):
        async with self._lock:
            with open(self.path, "w", encoding="utf-8") as f:
                f.truncate(0)
            self._last_seq = 0
