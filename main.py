"""Command-line version:  python main.py"""
from orderbook import OrderBook
from simulator import MarketSimulator

HELP = """Commands:
  buy <price> <qty> [ttl]     sell <price> <qty> [ttl]
  mbuy <qty>                  msell <qty>          (market orders)
  cancel <id>                 tick [n]             (advance time, expires orders)
  book                        trades               sim [n]      tree      quit"""

book = OrderBook()
sim = MarketSimulator(book)


def show_book():
    asks = book.depth("sell", 8)[::-1]
    print("\n  ASKS (price  qty  orders)")
    for p, q, c in asks:
        print(f"    {p:8.2f} {q:6} {c:4}")
    print(f"  --- spread: {book.spread()} ---")
    for p, q, c in book.depth("buy", 8):
        print(f"    {p:8.2f} {q:6} {c:4}")
    print("  BIDS")


def show_trades(ts):
    for t in ts:
        print(f"  TRADE #{t.seq}: {t.qty} @ {t.price}  (buy #{t.buy_id} / sell #{t.sell_id})")


print(HELP)
while True:
    try:
        parts = input("\n> ").split()
        if not parts:
            continue
        cmd, a = parts[0].lower(), parts[1:]
        if cmd in ("quit", "exit"):
            break
        elif cmd in ("buy", "sell"):
            o, t = book.place_limit(cmd, float(a[0]), int(a[1]), int(a[2]) if len(a) > 2 else None)
            print(f"  order #{o.id}, remaining {o.remaining}")
            show_trades(t)
        elif cmd in ("mbuy", "msell"):
            o, t = book.place_market("buy" if cmd == "mbuy" else "sell", int(a[0]))
            print(f"  filled {o.qty - o.remaining}/{o.qty}")
            show_trades(t)
        elif cmd == "cancel":
            print("  cancelled" if book.cancel(int(a[0])) else "  no such order")
        elif cmd == "tick":
            print("  expired:", book.advance_time(int(a[0]) if a else 1))
        elif cmd == "book":
            show_book()
        elif cmd == "trades":
            show_trades(book.trades[-10:])
        elif cmd == "sim":
            sim.run(int(a[0]) if a else 100)
            show_book()
        elif cmd == "tree":
            print(f"  bids: {book.bids.size} levels, height {book.bids.height()}, "
                  f"rotations {book.bids.rotations}, black-height {book.bids.check() if book.bids.size else 0}")
            print(f"  asks: {book.asks.size} levels, height {book.asks.height()}, "
                  f"rotations {book.asks.rotations}, black-height {book.asks.check() if book.asks.size else 0}")
        else:
            print(HELP)
    except (ValueError, IndexError) as e:
        print("  invalid input:", e)
