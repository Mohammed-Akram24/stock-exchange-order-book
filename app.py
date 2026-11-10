"""Web UI:  streamlit run app.py"""
import matplotlib.pyplot as plt
import streamlit as st

from benchmark import run_benchmark
from orderbook import OrderBook
from simulator import MarketSimulator
from visualize import benchmark_chart, depth_chart, draw_tree, price_chart

st.set_page_config(page_title="Stock Exchange Order Book", layout="wide")
st.title("Stock Exchange Order Book")
st.caption("Red-Black Trees hold price levels, FIFO queues give time priority, a Min-Heap expires orders.")

ss = st.session_state
if "book" not in ss:
    ss.book = OrderBook()
    ss.sim = MarketSimulator(ss.book)
    ss.log = []
book = ss.book


def show(fig):
    st.pyplot(fig)
    plt.close(fig)


tab1, tab2, tab3, tab4 = st.tabs(["Trade", "Simulation", "Tree view", "Benchmark"])

with tab1:
    c = st.columns(5)
    side = c[0].radio("Side", ["buy", "sell"], horizontal=True)
    kind = c[1].selectbox("Type", ["Limit", "Market"])
    price = c[2].number_input("Price", min_value=0.01, value=100.0, step=0.05, disabled=kind == "Market")
    qty = c[3].number_input("Quantity", min_value=1, value=10, step=1)
    ttl = c[4].number_input("Expires in (ticks, 0 = never)", min_value=0, value=0, step=10,
                            disabled=kind == "Market")
    b = st.columns(4)
    if b[0].button("Submit order"):
        if kind == "Limit":
            o, t = book.place_limit(side, price, int(qty), int(ttl) or None)
        else:
            o, t = book.place_market(side, int(qty))
        st.success(f"Order #{o.id}: {len(t)} trade(s), {o.qty - o.remaining} of {o.qty} filled")
    cid = b[1].number_input("Order id to cancel", min_value=1, value=1, step=1)
    if b[2].button("Cancel order"):
        st.info("Cancelled" if book.cancel(int(cid)) else "No such resting order")
    if b[3].button("Advance time by 10 ticks"):
        st.info(f"Expired orders: {book.advance_time(10)}")

    m = st.columns(4)
    m[0].metric("Best bid", book.best_bid())
    m[1].metric("Best ask", book.best_ask())
    m[2].metric("Spread", book.spread())
    m[3].metric("Clock", book.clock)

    l, r = st.columns(2)
    l.subheader("Bids")
    l.dataframe([{"Price": p, "Qty": q, "Orders": n} for p, q, n in book.depth("buy", 10)])
    r.subheader("Asks")
    r.dataframe([{"Price": p, "Qty": q, "Orders": n} for p, q, n in book.depth("sell", 10)])
    show(depth_chart(book))
    st.subheader("Recent trades")
    st.dataframe([{"#": t.seq, "Price": t.price, "Qty": t.qty, "Buy id": t.buy_id,
                   "Sell id": t.sell_id} for t in book.trades[-10:][::-1]])

with tab2:
    n = st.slider("Random events to generate", 10, 2000, 200)
    s1, s2 = st.columns(2)
    if s1.button("Run simulation"):
        ss.log = ss.sim.run(n)[-15:]
    if s2.button("Reset everything"):
        ss.book = OrderBook()
        ss.sim = MarketSimulator(ss.book)
        ss.log = []
        st.rerun()
    st.text("\n".join(ss.log) or "No events yet")
    show(price_chart(book.trades))

with tab3:
    which = st.radio("Tree", ["Bids", "Asks"], horizontal=True)
    tree = book.bids if which == "Bids" else book.asks
    k = st.columns(4)
    k[0].metric("Price levels", tree.size)
    k[1].metric("Height", tree.height())
    k[2].metric("Rotations so far", tree.rotations)
    k[3].metric("Black height", tree.check() if tree.size else 0)
    st.caption("check() verified all five Red-Black properties on the live tree.")
    show(draw_tree(tree, f"{which} price-level tree (red = red node, dark = black node)"))

with tab4:
    sizes = st.multiselect("Sizes", [500, 1000, 2000, 4000, 8000], default=[500, 1000, 2000, 4000])
    if st.button("Run benchmark") and sizes:
        with st.spinner("Running (plain BST on sorted input is slow by design)..."):
            rows = run_benchmark(tuple(sorted(sizes)))
        show(benchmark_chart(rows))
        st.dataframe(rows)
