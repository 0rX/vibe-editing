"""Vibe Editing ENCODE GATE — MACHINE-WIDE semaphore for video encode jobs.

Why this exists: parallel.py caps concurrent encodes PER CALL. But if 6 Claude sessions
are each running their own batches, every session honors "cap=3" while the machine sees
6x3 = 18 ffmpegs fighting over one GPU encode block. Result: severe contention, every
session feels "slow", total throughput drops.

This module gives the WHOLE MACHINE a single semaphore with N slots. Every encode job —
regardless of which session, which skill, which Python process spawned it — has to
acquire a slot before running. Implementation = Windows byte-range locks (`msvcrt.locking`)
on N tiny lockfiles. Works across processes, no daemon needed, and survives crashes:
Windows drops file locks when the owning handle closes, including on abnormal exit.

Default cap scales with core count (see SLOTS below). Override:
    VIBE_ENCODE_SLOTS=4   # raise the cap (test before trusting)
    VIBE_ENCODE_SLOTS=1   # serialize completely (debugging)

Use it as a context manager around ffmpeg calls:

    from encode_gate import gate
    with gate():
        subprocess.run(ffmpeg_cmd, check=True)

Inside parallel.run_commands(kind="encode") it's already wired — most skills get it free.
"""
import msvcrt
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path

from winenv import work_dir


def _default_slots() -> int:
    """How many concurrent encodes this machine tolerates.

    The Mac original hardcoded 3, tuned for the M3 Max's two media engines. Windows
    hardware varies enormously — a 4-core ultrabook with one Intel QSV block and a
    32-core workstation with NVENC are not the same machine — so scale with cores and
    clamp to a sane range. Hardware encoders have limited parallel sessions regardless
    of CPU, and software libx264 already threads across all cores, so a high cap helps
    nobody in either case.
    """
    cpu = os.cpu_count() or 4
    return max(2, min(4, cpu // 4))


SLOTS = int(os.environ.get("VIBE_ENCODE_SLOTS") or _default_slots())

# Lock dir lives in the shared scratch space so every session on the machine sees the
# same slots. Unlike the Mac original's /tmp this is NOT cleared on reboot, which is
# harmless: the lockfiles are empty and the locks themselves die with their processes.
SLOT_DIR = Path(os.environ.get("VIBE_ENCODE_SLOT_DIR") or work_dir("encode_slots"))

# msvcrt locks a byte RANGE rather than a whole file the way flock does. One byte at
# offset 0 is enough to make the lock exclusive, and Windows permits locking past EOF
# so the empty slot files need no content.
_LOCK_BYTES = 1


def _ensure_slots():
    SLOT_DIR.mkdir(parents=True, exist_ok=True)
    for i in range(SLOTS):
        f = SLOT_DIR / f"slot_{i}"
        if not f.exists():
            f.touch()
    # Allow the dir to grow if SLOTS was raised, but don't delete existing slot files.


def _try_lock(fd) -> bool:
    """Non-blocking exclusive lock on one byte. True if acquired."""
    try:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, _LOCK_BYTES)
        return True
    except OSError:
        # Windows raises OSError (EDEADLOCK/EACCES) when the range is already held,
        # where POSIX flock raised BlockingIOError. Both mean "slot taken".
        return False


def _unlock(fd):
    try:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, _LOCK_BYTES)
    except OSError:
        pass  # already released, or the handle is going away anyway


@contextmanager
def gate(timeout: float | None = None, poll: float = 0.25):
    """Acquire one of SLOTS encode slots, blocking until one frees.

    timeout: max seconds to wait for a slot. None = wait forever (default).
    poll: how often to retry while all slots are taken.

    Releases the slot automatically when the `with` block exits, even on exception.
    """
    _ensure_slots()
    start = time.monotonic()
    last_log = start
    fds = []  # we open all slot files once, lock the first one we can

    try:
        # Open every slot file once up-front; we'll try each non-blocking lock per pass.
        for i in range(SLOTS):
            fd = os.open(str(SLOT_DIR / f"slot_{i}"), os.O_RDWR | os.O_BINARY)
            fds.append(fd)

        while True:
            for fd in fds:
                if not _try_lock(fd):
                    continue  # try the next slot
                # Got a slot. Close the other fds so they don't leak.
                held_fd = fd
                for other in fds:
                    if other is not held_fd:
                        os.close(other)
                fds = [held_fd]
                try:
                    yield
                finally:
                    _unlock(held_fd)
                    os.close(held_fd)
                    fds = []
                return

            if timeout is not None and (time.monotonic() - start) > timeout:
                raise TimeoutError(f"encode_gate: no slot in {timeout}s (cap={SLOTS})")
            # Optional gentle stderr breadcrumb every ~30s so a stuck queue is visible.
            now = time.monotonic()
            if now - last_log > 30:
                try:
                    print(f"[encode_gate] waiting for a slot (cap={SLOTS}, waited {int(now-start)}s)",
                          file=sys.stderr)
                except Exception:
                    pass
                last_log = now
            time.sleep(poll)
    finally:
        # Defensive close on any error path.
        for fd in fds:
            try:
                os.close(fd)
            except Exception:
                pass


def stats():
    """Quick snapshot of slot state: how many free vs busy."""
    _ensure_slots()
    free = 0
    busy = 0
    for i in range(SLOTS):
        fd = os.open(str(SLOT_DIR / f"slot_{i}"), os.O_RDWR | os.O_BINARY)
        try:
            if _try_lock(fd):
                _unlock(fd)
                free += 1
            else:
                busy += 1
        finally:
            os.close(fd)
    return {"cap": SLOTS, "free": free, "busy": busy}


if __name__ == "__main__":
    import json
    print(json.dumps(stats(), indent=2))
