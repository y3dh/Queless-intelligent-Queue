"""Core data types for QUEUELESS."""

from dataclasses import dataclass, field

# Priority classes: lower number = served earlier
PRIORITY = {"emergency": 0, "senior": 1, "appointment": 2, "normal": 3}


@dataclass(order=True)
class Token:
    """A customer token. Ordering drives the min-heap:
    (priority class, arrival time, token id) -> lexicographic, so the
    comparison is O(1) and ties break deterministically (FIFO inside a class).
    """
    sort_key: tuple = field(init=False, repr=False)

    tid: int
    name: str
    category: str = "normal"
    arrival: int = 0          # minutes since opening
    service_time: int = 5     # estimated minutes at the counter

    def __post_init__(self):
        self.sort_key = (PRIORITY[self.category], self.arrival, self.tid)


@dataclass
class Counter:
    cid: int
    name: str
    speed: float = 1.0        # 1.0 = normal; 2.0 = twice as fast
    free_at: int = 0          # minute at which this counter becomes free

    def duration(self, token: Token) -> int:
        return max(1, round(token.service_time / self.speed))
