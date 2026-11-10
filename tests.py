"""Run:  python -m unittest tests -v"""
import math
import random
import unittest

from orderbook import OrderBook
from rbtree import RedBlackTree
from simulator import MarketSimulator


class TestRedBlackTree(unittest.TestCase):
    def test_random_insert_delete(self):
        rnd, t = random.Random(3), RedBlackTree()
        keys = rnd.sample(range(10000), 2000)
        for i, k in enumerate(keys):
            t.insert(k)
            if i % 100 == 0:
                t.check()
        self.assertEqual([n.key for n in t.items()], sorted(keys))
        for i, k in enumerate(keys[:1000]):
            self.assertTrue(t.delete(k))
            if i % 100 == 0:
                t.check()
        t.check()
        self.assertEqual(t.size, 1000)
        self.assertFalse(t.delete(-1))

    def test_sorted_input_stays_balanced(self):
        t = RedBlackTree()
        for k in range(1, 1024):
            t.insert(k)
        t.check()
        self.assertLessEqual(t.height(), 2 * math.log2(1024))


class TestOrderBook(unittest.TestCase):
    def test_price_priority(self):
        b = OrderBook()
        for p in (101, 100, 102):
            b.place_limit("sell", p, 5)
        _, trades = b.place_limit("buy", 101, 8)
        self.assertEqual([(t.price, t.qty) for t in trades], [(100, 5), (101, 3)])

    def test_time_priority(self):
        b = OrderBook()
        b.place_limit("sell", 100, 5)      # id 1
        b.place_limit("sell", 100, 5)      # id 2
        _, trades = b.place_limit("buy", 100, 5)
        self.assertEqual(trades[0].sell_id, 1)
        self.assertIn(2, b.orders)

    def test_partial_fill_rests(self):
        b = OrderBook()
        b.place_limit("sell", 100, 3)
        o, trades = b.place_limit("buy", 100, 10)
        self.assertEqual(sum(t.qty for t in trades), 3)
        self.assertEqual(b.best_bid(), 100)
        self.assertEqual(o.remaining, 7)

    def test_market_order(self):
        b = OrderBook()
        b.place_limit("sell", 100, 4)
        b.place_limit("sell", 101, 4)
        o, trades = b.place_market("buy", 10)
        self.assertEqual(o.qty - o.remaining, 8)
        self.assertIsNone(b.best_ask())

    def test_cancel_removes_level(self):
        b = OrderBook()
        o, _ = b.place_limit("buy", 99, 5)
        self.assertTrue(b.cancel(o.id))
        self.assertIsNone(b.best_bid())
        self.assertFalse(b.cancel(o.id))

    def test_expiry_heap(self):
        b = OrderBook()
        a, _ = b.place_limit("buy", 99, 5, ttl=10)
        c, _ = b.place_limit("buy", 98, 5, ttl=30)
        self.assertEqual(b.advance_time(10), [a.id])
        self.assertEqual(b.advance_time(25), [c.id])
        self.assertIsNone(b.best_bid())

    def test_simulation_invariants(self):
        b = OrderBook()
        sim = MarketSimulator(b, seed=7)
        for _ in range(3000):
            sim.step()
            if b.best_bid() is not None and b.best_ask() is not None:
                self.assertLess(b.best_bid(), b.best_ask())      # book never crossed
        b.bids.check()
        b.asks.check()
        level_total = sum(n.value.total for t in (b.bids, b.asks) for n in t.items())
        self.assertEqual(level_total, sum(o.remaining for o in b.orders.values()))


if __name__ == "__main__":
    unittest.main()
