"""
Hand-built binary min-heap used as the token priority queue.

DAA focus: array-based complete binary tree, sift-up / sift-down.
  push     O(log n)
  pop      O(log n)
  peek     O(1)
  heapify  O(n)   (bottom-up build, not n log n)
"""


class MinHeap:
    def __init__(self, items=None):
        self.a = list(items) if items else []
        if self.a:
            self._build()

    # ---- O(n) bottom-up build --------------------------------------
    def _build(self):
        for i in range(len(self.a) // 2 - 1, -1, -1):
            self._sift_down(i)

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self.a[i] < self.a[parent]:
                self.a[i], self.a[parent] = self.a[parent], self.a[i]
                i = parent
            else:
                break

    def _sift_down(self, i):
        n = len(self.a)
        while True:
            left, right, small = 2 * i + 1, 2 * i + 2, i
            if left < n and self.a[left] < self.a[small]:
                small = left
            if right < n and self.a[right] < self.a[small]:
                small = right
            if small == i:
                return
            self.a[i], self.a[small] = self.a[small], self.a[i]
            i = small

    # ---- public API -------------------------------------------------
    def push(self, item):
        self.a.append(item)
        self._sift_up(len(self.a) - 1)

    def pop(self):
        if not self.a:
            raise IndexError("pop from empty heap")
        top = self.a[0]
        last = self.a.pop()
        if self.a:
            self.a[0] = last
            self._sift_down(0)
        return top

    def peek(self):
        return self.a[0] if self.a else None

    def __len__(self):
        return len(self.a)

    def __bool__(self):
        return bool(self.a)
