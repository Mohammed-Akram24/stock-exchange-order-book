"""Random order-flow generator so the book can be demonstrated and benchmarked."""
import random


class MarketSimulator:
    def __init__(self, book, seed=42, start_price=100.0):
        self.book = book
        self.rnd = random.Random(seed)
        self.mid = start_price

    def step(self):
        r, b = self.rnd, self.book
        self.mid = max(1.0, self.mid + r.gauss(0, 0.15))
        roll = r.random()
        if roll < 0.70:
            side = r.choice(["buy", "sell"])
            off = abs(r.gauss(0, 1.0))
            price = round(self.mid - off if side == "buy" else self.mid + off, 2)
            ttl = r.randint(20, 200) if r.random() < 0.3 else None
            o, t = b.place_limit(side, max(0.01, price), r.randint(1, 50), ttl)
            msg = f"LIMIT {side} {o.qty} @ {o.price} -> {len(t)} trade(s)"
        elif roll < 0.85:
            side = r.choice(["buy", "sell"])
            o, t = b.place_market(side, r.randint(1, 30))
            msg = f"MARKET {side} {o.qty} -> {len(t)} trade(s)"
        elif b.orders:
            oid = r.choice(list(b.orders))
            b.cancel(oid)
            msg = f"CANCEL #{oid}"
        else:
            msg = "idle"
        expired = b.advance_time(1)
        if expired:
            msg += f" | {len(expired)} expired"
        return msg

    def run(self, n):
        return [self.step() for _ in range(n)]
