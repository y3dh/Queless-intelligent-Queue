"""
QUEUELESS web front-end.

Pure standard-library HTTP server — no pip installs. It serves index.html and
exposes one JSON endpoint, /api/run, which executes the DAA algorithms in
algorithms.py and returns the results.

    python3 server.py        ->  opens http://localhost:8000 in your browser
"""

import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from models import Token, Counter, PRIORITY
from algorithms import (
    dispatch_priority, sjf_order, fcfs_order, single_server_avg_wait,
    allocate_staff_dp, nearest_counter,
)

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 8000

FLOOR_PLAN = {
    "Entrance": {"Lobby": 4, "Corridor": 9},
    "Lobby": {"Entrance": 4, "Hall-A": 6, "Corridor": 2},
    "Corridor": {"Entrance": 9, "Lobby": 2, "Hall-B": 5},
    "Hall-A": {"Lobby": 6, "Counter-1": 2, "Counter-2": 4},
    "Hall-B": {"Corridor": 5, "Counter-3": 3},
    "Counter-1": {"Hall-A": 2},
    "Counter-2": {"Hall-A": 4},
    "Counter-3": {"Hall-B": 3},
}


def run_simulation(payload):
    tokens = [
        Token(tid=i + 1,
              name=t.get("name") or f"Token {i + 1}",
              category=t.get("category", "normal"),
              arrival=int(t.get("arrival", 0)),
              service_time=max(1, int(t.get("service_time", 5))))
        for i, t in enumerate(payload["tokens"])
    ]
    counters = [
        Counter(cid=i + 1, name=f"Counter-{i + 1}", speed=float(c["speed"]))
        for i, c in enumerate(payload["counters"])
    ]
    staff = int(payload.get("staff", 4))

    # 1. heap dispatch
    schedule, stats = dispatch_priority(tokens, counters)
    rows = [{
        "tid": tok.tid, "name": tok.name, "category": tok.category,
        "counter": cname, "arrival": tok.arrival,
        "start": start, "end": end, "wait": wait,
    } for tok, cname, start, end, wait in schedule]

    # 2. greedy SJF vs FCFS on one counter
    fcfs = single_server_avg_wait(fcfs_order(tokens))
    sjf = single_server_avg_wait(sjf_order(tokens))

    # 3. DP staff allocation (load = work actually dispatched to each counter)
    loads = [0.0] * len(counters)
    index = {c.name: i for i, c in enumerate(counters)}
    for tok, cname, _s, _e, _w in schedule:
        loads[index[cname]] += tok.service_time
    plan, total_cost = allocate_staff_dp(loads, staff)

    # 4. Dijkstra routing to the nearest open counter
    open_counters = [c.name for c in counters if c.name in FLOOR_PLAN]
    if open_counters:
        best, dist, path = nearest_counter(FLOOR_PLAN, "Entrance", open_counters)
    else:
        best, dist, path = None, 0, []

    return {
        "stats": stats,
        "schedule": rows,
        "counters": [{"name": c.name, "speed": c.speed} for c in counters],
        "greedy": {
            "fcfs": fcfs,
            "sjf": sjf,
            "improvement": (fcfs - sjf) / fcfs * 100 if fcfs else 0.0,
            "sjf_order": [{"name": t.name, "service_time": t.service_time}
                          for t in sjf_order(tokens)],
            "fcfs_order": [{"name": t.name, "service_time": t.service_time}
                           for t in fcfs_order(tokens)],
        },
        "allocation": {
            "staff": staff,
            "total_cost": total_cost,
            "rows": [{"counter": counters[i].name, "load": loads[i],
                      "extra": plan[i], "wait": loads[i] / (plan[i] + 1)}
                     for i in range(len(counters))],
        },
        "routing": {"target": best, "distance": dist, "path": path},
        "classes": list(PRIORITY),
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):          # quieter console
        pass

    def _send(self, code, body, ctype):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            with open(os.path.join(HERE, "index.html"), "rb") as fh:
                self._send(200, fh.read(), "text/html; charset=utf-8")
        else:
            self._send(404, "not found", "text/plain")

    def do_POST(self):
        if self.path != "/api/run":
            self._send(404, "not found", "text/plain")
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
            result = run_simulation(payload)
            self._send(200, json.dumps(result), "application/json")
        except Exception as exc:                       # surface errors in the UI
            self._send(400, json.dumps({"error": str(exc)}), "application/json")


def main():
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"QUEUELESS running at {url}   (press Ctrl+C to stop)")
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
