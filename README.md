# QUEUELESS — Intelligent Queue Management System
**Subject:** Design & Analysis of Algorithms (DAA) — mini project

## 1. Problem statement
Banks, hospitals and government offices lose time to physical queues: customers
wait without knowing their turn, counters sit idle while others overload, and
urgent cases get stuck behind routine ones. QUEUELESS replaces the physical line
with a token system that decides **who is served next, at which counter, by how
many staff, and where the customer should walk** — each decision driven by a
classical algorithm with a proven complexity bound.

## 2. Modules and algorithm design techniques

| # | Module | Technique | Algorithm |
|---|--------|-----------|-----------|
| 1 | Token dispatch | Data structure design | Binary min-heap (built from scratch) |
| 2 | Service ordering | Greedy | Shortest Job First vs FCFS |
| 3 | Staff allocation | Dynamic programming | Optimal partition of S staff over m counters |
| 4 | Counter routing | Graph / greedy | Dijkstra's shortest path |

### 2.1 Priority dispatch — two heaps
Each token carries the key `(priority_class, arrival_time, token_id)`, so
comparison is O(1) and ties inside a class fall back to FIFO (fairness).

* **Token heap** gives the most urgent waiting token in `O(log n)`.
* **Counter heap** keyed on `free_at` gives the earliest-free counter in `O(log m)`.

Every token is pushed and popped exactly once →
**T(n, m) = O((n + m) log n)**, space `O(n + m)`.
A naive "scan all tokens for the best one" dispatcher is `O(n²)`.

### 2.2 Greedy SJF — optimality argument
On a single counter, ordering jobs by non-decreasing service time minimises
average waiting time. *Exchange argument:* if a longer job `a` is placed before
a shorter job `b`, swapping them reduces `b`'s wait by `t(a) − t(b) > 0` and
raises no other job's wait; therefore no inversion can appear in an optimal
schedule. Cost = cost of sorting = **O(n log n)**.
Trade-off: pure SJF can starve long jobs, so QUEUELESS applies SJF *inside* a
priority class only — the heap guarantees urgent classes are never starved.

### 2.3 DP staff allocation
Counter *i* with pending load `L[i]` and `k` extra staff is predicted to take
`L[i] / (k + 1)` minutes. Minimise the total over all counters subject to
`Σ k = S`.

```
dp[i][s] = min over k = 0..s of  L[i]/(k+1) + dp[i+1][s-k]
dp[m][s] = 0
```

`m · S` states, `O(S)` work per state → **O(m · S²)** time, `O(m · S)` space.
Greedy "give all staff to the busiest counter" is not optimal here because the
marginal benefit of each extra employee shrinks as `1/(k+1)`; the DP captures
that overlapping-subproblem structure.

### 2.4 Dijkstra routing
The branch floor plan is a weighted graph (entrance, lobbies, halls, counters).
Dijkstra from the entrance to the set of *open* counters returns the nearest one
and the walking path. With the same binary heap: **O(E log V)**.

## 3. Complexity summary

| Operation | Time | Space |
|---|---|---|
| Heap push / pop | O(log n) | O(n) |
| Heapify (bottom-up build) | O(n) | O(n) |
| Priority dispatch | O((n + m) log n) | O(n + m) |
| Greedy SJF ordering | O(n log n) | O(n) |
| DP staff allocation | O(m · S²) | O(m · S) |
| Dijkstra routing | O(E log V) | O(V + E) |

## 4. Files
* `priority_queue.py` — binary min-heap written from scratch (sift-up/sift-down, O(n) heapify)
* `models.py` — `Token` and `Counter` data types, priority classes
* `algorithms.py` — the four algorithms above
* `main.py` — driver: runs all four modules on a 12-token, 3-counter branch
* `benchmark.py` — empirical growth check: heap dispatch vs naive O(n²)
* `server.py` — standard-library HTTP server exposing `/api/run` (no pip installs)
* `index.html` — web front-end: editable tokens/counters, Gantt chart, live results

## 5. How to run

**Web interface (recommended for the demo)**
```bash
cd ~/Desktop/queueless
python3 server.py
```
It opens <http://localhost:8000> automatically. Edit tokens, counters and staff on
the left, press **Run simulation**, and all four algorithms re-run in Python and
redraw. Press `Ctrl+C` in Terminal to stop the server.

**Command line**
```bash
python3 main.py
python3 benchmark.py
```
No external libraries — standard Python 3 only, so it runs on a stock Mac.

The front-end is only a view: every result on screen is computed by
`algorithms.py` on the server, so the complexity analysis below describes the
code that actually runs.

## 6. Sample result (12 tokens, 3 counters)
```
served = 12   avg wait = 7.42 min   max wait = 15 min   makespan = 40 min
FCFS average wait : 38.50 min
SJF  average wait : 32.58 min   -> 15.37 % improvement
nearest open counter : Counter-1 (12 m)  Entrance -> Lobby -> Hall-A -> Counter-1
```

## 6b. Benchmark — heap dispatch vs naive O(n^2)
```
      n     heap (ms)    naive (ms)   speedup
    500          3.58         17.08      4.8x
   1000          8.73         69.94      8.0x
   2000         18.29        279.50     15.3x
   4000         41.33       1132.02     27.4x
   8000         95.03       4544.86     47.8x
```
Each doubling of `n` roughly doubles the heap time but quadruples the naive
time, and the speedup itself doubles — exactly the `O(n log n)` vs `O(n^2)`
separation predicted by the analysis.

## 7. Conclusion
QUEUELESS shows how one practical system naturally needs three different design
paradigms: a **data structure** for the dispatch decision, a **greedy** rule for
ordering (with an optimality proof and a fairness caveat), and **dynamic
programming** where the greedy rule provably fails. The benchmark confirms the
`O(n log n)`-class behaviour of the heap dispatcher against the `O(n²)` baseline.
