"""
Race Condition Demo: Why Synchronization Matters
---------------------------------------------------
This demonstrates a classic concurrency bug: multiple threads incrementing
a shared counter WITHOUT a lock lose updates, because "x += 1" is not atomic
in Python -- it's actually three steps (read x, add 1, write x back), and
threads can interleave between those steps.

Run it a few times. The "unsafe" version usually gives a WRONG final count,
and the wrong count changes between runs because thread scheduling is
non-deterministic. The "safe" version always gives the correct count because
a threading.Lock ensures only one thread touches the counter at a time.

Usage:
    python race_condition_demo.py
"""

import threading
import time

NUM_THREADS = 8
INCREMENTS_PER_THREAD = 2_000


class UnsafeCounter:
    def __init__(self):
        self.count = 0

    def increment(self):
        # NOT atomic: read, add, write are 3 separate steps.
        # Another thread can run between any of these steps.
        # (A tiny sleep(0) yield widens that window so the race reliably
        # shows up here too -- the bug is real either way, this just
        # makes it visible instead of depending on scheduler luck.)
        current = self.count
        time.sleep(0)
        self.count = current + 1


class SafeCounter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:  # only one thread can be inside this block at a time
            current = self.count
            time.sleep(0)
            self.count = current + 1


def worker(counter, n):
    for _ in range(n):
        counter.increment()


def run_trial(counter_cls, label):
    counter = counter_cls()
    threads = [
        threading.Thread(target=worker, args=(counter, INCREMENTS_PER_THREAD))
        for _ in range(NUM_THREADS)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    expected = NUM_THREADS * INCREMENTS_PER_THREAD
    status = "CORRECT" if counter.count == expected else "WRONG (lost updates!)"
    print(f"{label:30s} expected={expected:,}  got={counter.count:,}  -> {status}")


def main():
    print(f"{NUM_THREADS} threads x {INCREMENTS_PER_THREAD:,} increments each\n")
    run_trial(UnsafeCounter, "Without lock (unsafe)")
    run_trial(SafeCounter, "With lock (synchronized)")


if __name__ == "__main__":
    main()
