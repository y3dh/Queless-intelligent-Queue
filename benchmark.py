"""Empirical check: heap dispatcher vs naive linear-scan dispatcher."""

import random
import time

from models import Token, Counter
from algorithms import dispatch_priority
from models import PRIORITY


def naive_dispatch(tokens, counters):
    """O(n^2 + n*m): rescan every waiting token and every counter each round."""
    pending = list(tokens)
    for c in counters:
        c.free_at = 0
    schedule = []
    while pending:
        best = min(pending, key=lambda t: t.sort_key)   # O(n) scan
        pending.remove(best)                            # O(n)
        c = min(counters, key=lambda c: c.free_at)      # O(m) scan
        start = max(c.free_at, best.arrival)
        c.free_at = start + c.duration(best)
        schedule.append((best, c.name, start, c.free_at, start - best.arrival))
    return schedule


def make(n):
    cats = list(PRIORITY)
    random.seed(1)
    return [Token(i, f"c{i}", random.choice(cats),
                  random.randint(0, n), random.randint(1, 15)) for i in range(n)]


def timed(fn, tokens, counters):
    t0 = time.perf_counter()
    fn(tokens, counters)
    return (time.perf_counter() - t0) * 1000


print(f"{'n':>7}{'heap (ms)':>14}{'naive (ms)':>14}{'speedup':>10}")
for n in (500, 1000, 2000, 4000, 8000):
    toks = make(n)
    cs = lambda: [Counter(i, f"C{i}", 1.0 + 0.1 * i) for i in range(5)]
    h = timed(dispatch_priority, list(toks), cs())
    nv = timed(naive_dispatch, list(toks), cs())
    print(f"{n:>7}{h:>14.2f}{nv:>14.2f}{nv / h:>9.1f}x")
