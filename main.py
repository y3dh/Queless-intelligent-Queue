"""
QUEUELESS — Intelligent Queue Management System
Design & Analysis of Algorithms mini project.

Run:  python3 main.py
"""

import random

from models import Token, Counter
from algorithms import (
    dispatch_priority, sjf_order, fcfs_order, single_server_avg_wait,
    allocate_staff_dp, nearest_counter,
)

LINE = "-" * 68


def demo_tokens():
    names = ["Asha", "Bilal", "Chandu", "Divya", "Eshan", "Farah",
             "Gopi", "Hiba", "Irfan", "Jaya", "Kiran", "Latha"]
    cats = ["normal", "normal", "normal", "senior", "appointment", "emergency"]
    random.seed(7)
    return [
        Token(tid=i + 1, name=n, category=random.choice(cats),
              arrival=random.randint(0, 25), service_time=random.randint(3, 12))
        for i, n in enumerate(names)
    ]


def part1_dispatch(tokens, counters):
    print(LINE)
    print("1) PRIORITY DISPATCH  (binary min-heap, O((n+m) log n))")
    print(LINE)
    schedule, stats = dispatch_priority(tokens, counters)
    print(f"{'TOK':<5}{'NAME':<9}{'CLASS':<13}{'COUNTER':<12}"
          f"{'ARR':>4}{'START':>7}{'END':>5}{'WAIT':>6}")
    for tok, cname, start, end, wait in schedule:
        print(f"{tok.tid:<5}{tok.name:<9}{tok.category:<13}{cname:<12}"
              f"{tok.arrival:>4}{start:>7}{end:>5}{wait:>6}")
    print(f"\nserved={stats['served']}  avg wait={stats['avg_wait']:.2f} min"
          f"  max wait={stats['max_wait']} min"
          f"  makespan={stats['makespan']} min")
    return stats


def part2_greedy(tokens):
    print()
    print(LINE)
    print("2) GREEDY SJF vs FCFS  (single counter, O(n log n))")
    print(LINE)
    f = single_server_avg_wait(fcfs_order(tokens))
    s = single_server_avg_wait(sjf_order(tokens))
    print(f"FCFS average wait : {f:7.2f} min")
    print(f"SJF  average wait : {s:7.2f} min")
    print(f"improvement       : {(f - s) / f * 100:7.2f} %")
    print("SJF order         : " +
          ", ".join(f"{t.name}({t.service_time})" for t in sjf_order(tokens)))


def part3_dp(counters, tokens):
    print()
    print(LINE)
    print("3) DP STAFF ALLOCATION  (O(m*S^2))")
    print(LINE)
    loads = [0.0] * len(counters)
    for i, t in enumerate(tokens):                 # round-robin load estimate
        loads[i % len(counters)] += t.service_time
    staff = 4
    plan, cost = allocate_staff_dp(loads, staff)
    for c, l, k in zip(counters, loads, plan):
        print(f"{c.name:<12} load={l:5.0f} min  extra staff={k}"
              f"  -> predicted wait {l / (k + 1):6.2f} min")
    print(f"\n{staff} floating staff placed; total predicted wait = {cost:.2f} min")


def part4_routing():
    print()
    print(LINE)
    print("4) DIJKSTRA COUNTER ROUTING  (O(E log V))")
    print(LINE)
    graph = {
        "Entrance": {"Lobby": 4, "Corridor": 9},
        "Lobby":    {"Entrance": 4, "Hall-A": 6, "Corridor": 2},
        "Corridor": {"Entrance": 9, "Lobby": 2, "Hall-B": 5},
        "Hall-A":   {"Lobby": 6, "Counter-1": 2, "Counter-2": 4},
        "Hall-B":   {"Corridor": 5, "Counter-3": 3},
        "Counter-1": {"Hall-A": 2},
        "Counter-2": {"Hall-A": 4},
        "Counter-3": {"Hall-B": 3},
    }
    open_counters = ["Counter-1", "Counter-2", "Counter-3"]
    best, dist, path = nearest_counter(graph, "Entrance", open_counters)
    print(f"nearest open counter : {best}  ({dist} m)")
    print("walking path         : " + " -> ".join(path))


def main():
    print("=" * 68)
    print("QUEUELESS — Intelligent Queue Management System".center(68))
    print("Design & Analysis of Algorithms — mini project".center(68))
    print("=" * 68)

    tokens = demo_tokens()
    counters = [Counter(1, "Counter-1", 1.0),
                Counter(2, "Counter-2", 1.5),
                Counter(3, "Counter-3", 0.8)]

    part1_dispatch(tokens, counters)
    part2_greedy(tokens)
    part3_dp(counters, tokens)
    part4_routing()

    print()
    print(LINE)
    print("COMPLEXITY SUMMARY")
    print(LINE)
    rows = [
        ("Heap push / pop",        "O(log n)",     "O(n)"),
        ("Heapify (build)",        "O(n)",         "O(n)"),
        ("Priority dispatch",      "O((n+m) log n)", "O(n+m)"),
        ("Greedy SJF ordering",    "O(n log n)",   "O(n)"),
        ("DP staff allocation",    "O(m*S^2)",     "O(m*S)"),
        ("Dijkstra routing",       "O(E log V)",   "O(V+E)"),
    ]
    print(f"{'MODULE':<24}{'TIME':<18}{'SPACE'}")
    for a, b, c in rows:
        print(f"{a:<24}{b:<18}{c}")
    print(LINE)


if __name__ == "__main__":
    main()
