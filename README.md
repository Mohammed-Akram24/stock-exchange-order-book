# Stock Exchange Order Book (IF3151 - Advanced Data Structures and Algorithms)

A limit order book that matches buy and sell orders by price-time priority.

## Setup
1. Python 3.9 or newer (tick "Add Python to PATH" on Windows)
2. `pip install -r requirements.txt`

## Run
- Web UI:     `streamlit run app.py`
- Command line: `python main.py`
- Tests:      `python -m unittest tests -v`

## Data structures
| Part | Structure | Cost |
|---|---|---|
| Bid / ask price levels | Red-Black Tree (own implementation) | insert, delete, find O(log n) |
| Best bid / best ask | max / min node of the tree | O(log n) |
| Orders at one price | FIFO queue (OrderedDict) | O(1) add, cancel, match |
| Order expiry | Binary Min-Heap (own implementation) | push, pop O(log n) |
| Order lookup by id | Hash table (dict) | O(1) |

## Files
rbtree.py | heap.py | orderbook.py | simulator.py | benchmark.py | visualize.py | main.py | app.py | tests.py

## Viva questions
1. Why a Red-Black Tree and not a plain BST? Orders arrive with trending prices, which degrades a BST to O(n); an RB tree keeps height <= 2*log2(n+1).
2. Why not a sorted list? Insertion shifts elements, O(n). The benchmark tab shows it.
3. Why a heap for expiry? We only ever need the earliest expiry time: peek O(1), pop O(log n).
4. Why store a queue per price level? Orders at equal price must fill in arrival order (time priority).
5. What happens when a price level empties? Its node is deleted from the tree, which triggers the Red-Black delete fix-up.
6. Which RB insert cases exist? Uncle red (recolour), uncle black triangle (rotate then case 3), uncle black line (one rotation).
7. Is cancel O(log n)? Yes: dict lookup O(1), tree find O(log n), O(1) removal from the level, O(log n) if the level is deleted.
