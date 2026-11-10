"""Matplotlib drawings: tree, market depth, trade prices, benchmark."""
import math

import matplotlib.pyplot as plt

from rbtree import RED


def draw_tree(tree, title="", max_depth=5):
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.axis("off")
    ax.set_title(title)
    if tree.root is tree.NIL:
        ax.text(0.5, 0.5, "(empty tree)", ha="center")
        return fig
    pos, counter = {}, [0]

    def layout(n, d):
        if n is tree.NIL or d > max_depth:
            return
        layout(n.left, d + 1)
        pos[n] = (counter[0], -d)
        counter[0] += 1
        layout(n.right, d + 1)

    layout(tree.root, 0)
    for n, (x, y) in pos.items():
        for c in (n.left, n.right):
            if c in pos:
                ax.plot([x, pos[c][0]], [y, pos[c][1]], color="#888", zorder=1)
    for n, (x, y) in pos.items():
        ax.scatter([x], [y], s=650, color="#c0392b" if n.color == RED else "#222", zorder=2)
        ax.text(x, y, f"{n.key:g}", color="white", ha="center", va="center", fontsize=7, zorder=3)
    if tree.height() > max_depth + 1:
        ax.text(0.99, 0.02, f"Showing top {max_depth + 1} levels of {tree.height()}",
                transform=ax.transAxes, ha="right", fontsize=8)
    return fig


def depth_chart(book, levels=15):
    fig, ax = plt.subplots(figsize=(8, 3.5))
    for side, color in (("buy", "#27ae60"), ("sell", "#c0392b")):
        d = book.depth(side, levels)
        if d:
            prices = [p for p, _, _ in d]
            cum, run = [], 0
            for _, q, _ in d:
                run += q
                cum.append(run)
            ax.step(prices, cum, where="post", color=color, label="Bids" if side == "buy" else "Asks")
            ax.fill_between(prices, cum, step="post", color=color, alpha=0.2)
    ax.set_xlabel("Price")
    ax.set_ylabel("Cumulative quantity")
    ax.set_title("Market depth")
    ax.legend()
    fig.tight_layout()
    return fig


def price_chart(trades):
    fig, ax = plt.subplots(figsize=(8, 3))
    if trades:
        ax.plot([t.price for t in trades], color="#2980b9")
    ax.set_xlabel("Trade #")
    ax.set_ylabel("Price")
    ax.set_title("Traded price")
    fig.tight_layout()
    return fig


def benchmark_chart(rows):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, key, title in zip(axes, ("insert_ms", "search_ms", "height"),
                              ("Insert time (ms)", "500 searches (ms)", "Tree height")):
        for name in sorted({r["structure"] for r in rows}):
            for inp, style in (("random", "-"), ("sorted", "--")):
                pts = [(r["n"], r[key]) for r in rows
                       if r["structure"] == name and r["input"] == inp and r[key] is not None]
                if pts:
                    ax.plot(*zip(*pts), style, marker="o", label=f"{name} ({inp})")
        if key == "height":
            ns = sorted({r["n"] for r in rows})
            ax.plot(ns, [2 * math.log2(n + 1) for n in ns], ":", color="black", label="2·log2(n+1) bound")
        ax.set_title(title)
        ax.set_xlabel("n (keys)")
        ax.set_yscale("log")
    axes[0].legend(fontsize=7)
    fig.tight_layout()
    return fig
