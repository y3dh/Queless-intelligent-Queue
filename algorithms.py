"""
QUEUELESS algorithm core — the DAA content of the project.

1. dispatch_priority  : heap-based priority dispatch        O((n+m) log n)
2. sjf_order          : greedy Shortest-Job-First           O(n log n)
3. fcfs_order         : baseline First-Come-First-Serve     O(n log n)
4. allocate_staff_dp  : DP staff allocation across counters O(m * S^2)
5. nearest_counter    : Dijkstra routing inside the branch  O(E log V)
"""

from priority_queue import MinHeap
from models import Counter

INF = float("inf")


# ---------------------------------------------------------------- 1
def dispatch_priority(tokens, counters):
    """Assign every token to a counter, honouring priority class.

    Two heaps:
      * token heap     -> next most urgent token      (O(log n))
      * counter heap   -> earliest-free counter       (O(log m))
    Each token is pushed/popped once => O((n + m) log n).

    Returns (schedule, stats) where schedule rows are
    (token, counter_name, start, end, wait).
    """
    waiting = MinHeap(tokens)
    free = MinHeap([(c.free_at, c.cid, c) for c in counters])
    schedule = []

    while waiting:
        tok = waiting.pop()
        free_at, cid, counter = free.pop()
        start = max(free_at, tok.arrival)        # a counter cannot start early
        end = start + counter.duration(tok)
        schedule.append((tok, counter.name, start, end, start - tok.arrival))
        free.push((end, cid, counter))

    waits = [row[4] for row in schedule]
    stats = {
        "served": len(schedule),
        "avg_wait": sum(waits) / len(waits) if waits else 0.0,
        "max_wait": max(waits) if waits else 0,
        "makespan": max((row[3] for row in schedule), default=0),
    }
    return schedule, stats


# ---------------------------------------------------------------- 2,3
def sjf_order(tokens):
    """Greedy SJF. Sorting by service time minimises average waiting time
    on a single server (classic exchange-argument proof).  O(n log n)."""
    return sorted(tokens, key=lambda t: (t.service_time, t.arrival, t.tid))


def fcfs_order(tokens):
    """Baseline FCFS, for comparison.  O(n log n)."""
    return sorted(tokens, key=lambda t: (t.arrival, t.tid))


def single_server_avg_wait(order):
    """Average waiting time if `order` is served back-to-back on one counter."""
    clock, total = 0, 0
    for t in order:
        start = max(clock, t.arrival)
        total += start - t.arrival
        clock = start + t.service_time
    return total / len(order) if order else 0.0


# ---------------------------------------------------------------- 4
def allocate_staff_dp(loads, staff):
    """Distribute `staff` extra employees over counters to minimise total
    predicted wait.  Counter i with load L and k extra staff costs
    L / (k + 1) minutes (more staff -> parallel service).

    DP over (counter index, staff still available):
        dp[i][s] = min over k<=s of cost(i,k) + dp[i+1][s-k]
    States: m*S, transition O(S)  =>  time O(m*S^2), space O(m*S).
    """
    m = len(loads)
    dp = [[INF] * (staff + 1) for _ in range(m + 1)]
    choice = [[0] * (staff + 1) for _ in range(m + 1)]
    for s in range(staff + 1):
        dp[m][s] = 0.0

    for i in range(m - 1, -1, -1):
        for s in range(staff + 1):
            best, best_k = INF, 0
            for k in range(s + 1):
                cost = loads[i] / (k + 1) + dp[i + 1][s - k]
                if cost < best:
                    best, best_k = cost, k
            dp[i][s] = best
            choice[i][s] = best_k

    plan, s = [], staff
    for i in range(m):
        k = choice[i][s]
        plan.append(k)
        s -= k
    return plan, dp[0][staff]


# ---------------------------------------------------------------- 5
def nearest_counter(graph, source, targets):
    """Dijkstra from the entrance to the set of open counters, so the app can
    tell a customer *where to walk*.  O(E log V) with a binary heap."""
    dist = {v: INF for v in graph}
    dist[source] = 0
    prev = {}
    pq = MinHeap([(0, source)])
    done = set()

    while pq:
        d, u = pq.pop()
        if u in done:
            continue
        done.add(u)
        for v, w in graph[u].items():
            nd = d + w
            if nd < dist[v]:
                dist[v], prev[v] = nd, u
                pq.push((nd, v))

    best = min(targets, key=lambda t: dist.get(t, INF))
    path, cur = [], best
    while cur != source:
        path.append(cur)
        cur = prev[cur]
    path.append(source)
    return best, dist[best], path[::-1]
