"""Limit order book with price-time priority matching.

Bids  : Red-Black Tree keyed by price, best bid  = maximum node
Asks  : Red-Black Tree keyed by price, best ask  = minimum node
Level : FIFO queue of orders at one price (time priority)
Expiry: Min-Heap of (expiry_time, order_id)
"""
from collections import OrderedDict
from dataclasses import dataclass
from itertools import islice
from typing import Optional

from heap import MinHeap
from rbtree import RedBlackTree


@dataclass
class Order:
    id: int
    side: str                    # "buy" or "sell"
    price: Optional[float]       # None for market orders
    qty: int
    remaining: int
    expiry: Optional[int] = None


@dataclass
class Trade:
    seq: int
    price: float
    qty: int
    buy_id: int
    sell_id: int


class PriceLevel:
    def __init__(self, price):
        self.price = price
        self.orders = OrderedDict()     # insertion order = arrival order
        self.total = 0

    def add(self, o):
        self.orders[o.id] = o
        self.total += o.remaining

    def first(self):
        return next(iter(self.orders.values()))

    def remove(self, oid):
        o = self.orders.pop(oid)
        self.total -= o.remaining
        return o

    def fill(self, o, qty):
        o.remaining -= qty
        self.total -= qty
        if o.remaining == 0:
            del self.orders[o.id]


class OrderBook:
    def __init__(self):
        self.bids = RedBlackTree()
        self.asks = RedBlackTree()
        self.orders = {}                # resting orders by id
        self.expiry_heap = MinHeap()
        self.trades = []
        self.clock = 0
        self._next_id = 1

    # ---------- public API ----------
    def place_limit(self, side, price, qty, ttl=None):
        if side not in ("buy", "sell") or qty <= 0 or price <= 0:
            raise ValueError("invalid order")
        price = round(price, 2)
        expiry = self.clock + ttl if ttl else None
        order = self._new_order(side, price, qty, expiry)
        trades = self._match(order, price)
        if order.remaining > 0:
            self._rest(order)
        return order, trades

    def place_market(self, side, qty):
        """Fills against the book; any unfilled remainder is discarded."""
        if side not in ("buy", "sell") or qty <= 0:
            raise ValueError("invalid order")
        order = self._new_order(side, None, qty, None)
        return order, self._match(order, None)

    def cancel(self, order_id):
        order = self.orders.pop(order_id, None)
        if order is None:
            return False
        tree = self.bids if order.side == "buy" else self.asks
        node = tree.find(order.price)
        node.value.remove(order_id)
        if not node.value.orders:
            tree.delete(order.price)
        return True

    def advance_time(self, ticks=1):
        """Move the clock; the heap yields every order whose expiry has passed."""
        self.clock += ticks
        expired = []
        while len(self.expiry_heap) and self.expiry_heap.peek()[0] <= self.clock:
            _, oid = self.expiry_heap.pop()
            if self.cancel(oid):
                expired.append(oid)
        return expired

    def best_bid(self):
        n = self.bids.max_node()
        return n.key if n else None

    def best_ask(self):
        n = self.asks.min_node()
        return n.key if n else None

    def spread(self):
        b, a = self.best_bid(), self.best_ask()
        return round(a - b, 2) if b is not None and a is not None else None

    def depth(self, side, n=10):
        """Top n price levels as (price, total_qty, order_count)."""
        tree, rev = (self.bids, True) if side == "buy" else (self.asks, False)
        return [(nd.key, nd.value.total, len(nd.value.orders))
                for nd in islice(tree.items(reverse=rev), n)]

    # ---------- internals ----------
    def _new_order(self, side, price, qty, expiry):
        o = Order(self._next_id, side, price, qty, qty, expiry)
        self._next_id += 1
        return o

    def _rest(self, order):
        tree = self.bids if order.side == "buy" else self.asks
        node = tree.find(order.price) or tree.insert(order.price, PriceLevel(order.price))
        node.value.add(order)
        self.orders[order.id] = order
        if order.expiry is not None:
            self.expiry_heap.push((order.expiry, order.id))

    def _match(self, order, limit):
        trades = []
        book = self.asks if order.side == "buy" else self.bids
        while order.remaining > 0:
            node = book.min_node() if order.side == "buy" else book.max_node()
            if node is None:
                break
            if limit is not None and ((order.side == "buy" and node.key > limit) or
                                      (order.side == "sell" and node.key < limit)):
                break
            level = node.value
            resting = level.first()                       # earliest order at best price
            qty = min(order.remaining, resting.remaining)
            order.remaining -= qty
            level.fill(resting, qty)
            if resting.remaining == 0:
                self.orders.pop(resting.id, None)
            if not level.orders:
                book.delete(node.key)                     # Red-Black deletion
            buy_id, sell_id = ((order.id, resting.id) if order.side == "buy"
                               else (resting.id, order.id))
            t = Trade(len(self.trades) + 1, resting.price, qty, buy_id, sell_id)
            self.trades.append(t)
            trades.append(t)
        return trades
