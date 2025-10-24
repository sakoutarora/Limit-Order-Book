# persistence/snapshot.py
import os
import tempfile
import pickle
import shutil
import asyncio
from typing import Any
from datetime import datetime

class SnapshotManager:
    """
    Manage atomic snapshots. Each snapshot filename encodes last WAL seq:
      snapshot.{seq}.pkl
    """
    def __init__(self, dirpath: str):
        os.makedirs(dirpath, exist_ok=True)
        self.dirpath = dirpath
        self._lock = asyncio.Lock()

    def _snapshot_path(self, seq: int) -> str:
        return os.path.join(self.dirpath, f"snapshot.{seq}.pkl")

    def latest_snapshot(self):
        files = [f for f in os.listdir(self.dirpath) if f.startswith("snapshot.")]
        best = None
        best_seq = 0
        for f in files:
            try:
                seq = int(f.split(".")[1])
                if seq > best_seq:
                    best_seq = seq
                    best = os.path.join(self.dirpath, f)
            except Exception:
                continue
        if best:
            print(best_seq, best)
            return best_seq, best
        return 0, None

    async def write_snapshot(self, state: Any):
        """
        Atomically write state to snapshot.{wal_seq}.pkl
        """
        async with self._lock:
            target = self._snapshot_path(int(datetime.now().timestamp() * 1000))  
            fd, tmp = tempfile.mkstemp(dir=self.dirpath, prefix=".snap_tmp_")
            try:
                with os.fdopen(fd, "wb") as f:
                    pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
                    f.flush()
                    os.fsync(f.fileno())
                # atomic move
                shutil.move(tmp, target)
                # optionally remove older snapshots (keep last 2)
                self._cleanup_keep_latest(keep=2)
            finally:
                if os.path.exists(tmp):
                    os.remove(tmp)

    def _cleanup_keep_latest(self, keep=2):
        snaps = []
        for f in os.listdir(self.dirpath):
            if f.startswith("snapshot."):
                try:
                    seq = int(f.split(".")[1])
                    snaps.append((seq, os.path.join(self.dirpath, f)))
                except:
                    pass
        snaps.sort(reverse=True)
        for seq, path in snaps[keep:]:
            try:
                os.remove(path)
            except:
                pass

    async def load_latest(self):
        """
        Return tuple (wal_seq, state) or (0, None) if none.
        """
        seq, path = self.latest_snapshot()
        if not path:
            return 0, None
        with open(path, "rb") as f:
            state = pickle.load(f)
        return seq, state