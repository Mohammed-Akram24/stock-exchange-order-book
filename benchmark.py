"""Why balance matters: Red-Black Tree vs plain BST vs sorted list. (Unit I analysis)"""
import random
import time
from bisect import bisect_left, insort

from rbtree import RedBlackTree


class _N:
    __slots__ = ("key", "left", "right")

    def __init__(self, key):
        self.key, self.left, self.right = key, None, None


class UnbalancedBST:
    def __init__(self):
        self.root = None

    def insert(self, key):
        if self.root is None:
            self.root = _N(key)
            return
        n = self.root
        while True:
            if key == n.key:
                return
            side = "left" if key < n.key else "right"
            nxt = getattr(n, side)
            if nxt is None:
                setattr(n, side, _N(key))
                return
            n = nxt

    def find(self, key):
        n = self.root
        while n:
            if key == n.key:
                return n
            n = n.left if key < n.key else n.right
        return None

    def height(self):
        level, h = ([self.root] if self.root else []), 0
        while level:
            h += 1
            level = [c for n in level for c in (n.left, n.right) if c]
        return h


class SortedListIndex:
    def __init__(self):
        self.a = []

    def insert(self, key):
        insort(self.a, key)                  # O(n) shifting

    def find(self, key):
        i = bisect_left(self.a, key)
        return i < len(self.a) and self.a[i] == key

    def height(self):
        return None


class _RB(RedBlackTree):
    def insert(self, key, value=None):
        return super().insert(key, value)


STRUCTURES = {"Red-Black Tree": _RB, "Plain BST": UnbalancedBST, "Sorted list": SortedListIndex}


def run_benchmark(sizes=(500, 1000, 2000, 4000), seed=1):
    rows = []
    for n in sizes:
        rnd = random.Random(seed)
        keys = rnd.sample(range(n * 10), n)
        for order_name, seq in (("random", keys), ("sorted", sorted(keys))):
            probes = rnd.sample(seq, min(n, 500))
            for name, make in STRUCTURES.items():
                s = make()
                t0 = time.perf_counter()
                for k in seq:
                    s.insert(k)
                t1 = time.perf_counter()
                for k in probes:
                    s.find(k)
                t2 = time.perf_counter()
                rows.append({"structure": name, "input": order_name, "n": n,
                             "insert_ms": round((t1 - t0) * 1000, 2),
                             "search_ms": round((t2 - t1) * 1000, 2),
                             "height": s.height()})
    return rows
