"""Red-Black Tree written from scratch (CLRS), used for the price levels. (Unit III)

Properties: root is black; red nodes have black children; every root-to-leaf
path has the same number of black nodes  ->  height <= 2*log2(n+1).
"""
RED, BLACK = True, False


class Node:
    __slots__ = ("key", "value", "color", "left", "right", "parent")

    def __init__(self, key=None, value=None, color=BLACK):
        self.key, self.value, self.color = key, value, color
        self.left = self.right = self.parent = None


class RedBlackTree:
    def __init__(self):
        self.NIL = Node()                       # shared black sentinel leaf
        self.NIL.left = self.NIL.right = self.NIL.parent = self.NIL
        self.root = self.NIL
        self.size = 0
        self.rotations = 0

    # ---------- rotations ----------
    def _left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left is not self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is self.NIL:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
        self.rotations += 1

    def _right_rotate(self, x):
        y = x.left
        x.left = y.right
        if y.right is not self.NIL:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is self.NIL:
            self.root = y
        elif x is x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y
        self.rotations += 1

    # ---------- search ----------
    def find(self, key):
        n = self.root
        while n is not self.NIL:
            if key == n.key:
                return n
            n = n.left if key < n.key else n.right
        return None

    def _min(self, x):
        while x.left is not self.NIL:
            x = x.left
        return x

    def min_node(self):
        return None if self.root is self.NIL else self._min(self.root)

    def max_node(self):
        if self.root is self.NIL:
            return None
        x = self.root
        while x.right is not self.NIL:
            x = x.right
        return x

    # ---------- insertion ----------
    def insert(self, key, value=None):
        y, x = self.NIL, self.root
        while x is not self.NIL:
            y = x
            if key == x.key:
                x.value = value
                return x
            x = x.left if key < x.key else x.right
        z = Node(key, value, RED)
        z.left = z.right = self.NIL
        z.parent = y
        if y is self.NIL:
            self.root = z
        elif key < y.key:
            y.left = z
        else:
            y.right = z
        self.size += 1
        self._insert_fixup(z)
        return z

    def _insert_fixup(self, z):
        while z.parent.color == RED:
            gp = z.parent.parent
            if z.parent is gp.left:
                uncle = gp.right
                if uncle.color == RED:                  # case 1: recolour
                    z.parent.color = uncle.color = BLACK
                    gp.color = RED
                    z = gp
                else:
                    if z is z.parent.right:             # case 2: rotate to case 3
                        z = z.parent
                        self._left_rotate(z)
                    z.parent.color = BLACK              # case 3
                    z.parent.parent.color = RED
                    self._right_rotate(z.parent.parent)
            else:
                uncle = gp.left
                if uncle.color == RED:
                    z.parent.color = uncle.color = BLACK
                    gp.color = RED
                    z = gp
                else:
                    if z is z.parent.left:
                        z = z.parent
                        self._right_rotate(z)
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self._left_rotate(z.parent.parent)
        self.root.color = BLACK

    # ---------- deletion ----------
    def _transplant(self, u, v):
        if u.parent is self.NIL:
            self.root = v
        elif u is u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def delete(self, key):
        z = self.find(key)
        if z is None:
            return False
        y, y_color = z, z.color
        if z.left is self.NIL:
            x = z.right
            self._transplant(z, z.right)
        elif z.right is self.NIL:
            x = z.left
            self._transplant(z, z.left)
        else:
            y = self._min(z.right)
            y_color = y.color
            x = y.right
            if y.parent is z:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
        self.size -= 1
        if y_color == BLACK:
            self._delete_fixup(x)
        return True

    def _delete_fixup(self, x):
        while x is not self.root and x.color == BLACK:
            if x is x.parent.left:
                w = x.parent.right
                if w.color == RED:
                    w.color = BLACK
                    x.parent.color = RED
                    self._left_rotate(x.parent)
                    w = x.parent.right
                if w.left.color == BLACK and w.right.color == BLACK:
                    w.color = RED
                    x = x.parent
                else:
                    if w.right.color == BLACK:
                        w.left.color = BLACK
                        w.color = RED
                        self._right_rotate(w)
                        w = x.parent.right
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.right.color = BLACK
                    self._left_rotate(x.parent)
                    x = self.root
            else:
                w = x.parent.left
                if w.color == RED:
                    w.color = BLACK
                    x.parent.color = RED
                    self._right_rotate(x.parent)
                    w = x.parent.left
                if w.right.color == BLACK and w.left.color == BLACK:
                    w.color = RED
                    x = x.parent
                else:
                    if w.left.color == BLACK:
                        w.right.color = BLACK
                        w.color = RED
                        self._left_rotate(w)
                        w = x.parent.left
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.left.color = BLACK
                    self._right_rotate(x.parent)
                    x = self.root
        x.color = BLACK

    # ---------- utilities ----------
    def items(self, reverse=False):
        """In-order traversal (ascending, or descending if reverse)."""
        stack, n = [], self.root
        while stack or n is not self.NIL:
            if n is not self.NIL:
                stack.append(n)
                n = n.right if reverse else n.left
            else:
                n = stack.pop()
                yield n
                n = n.left if reverse else n.right

    def height(self):
        level, h = ([] if self.root is self.NIL else [self.root]), 0
        while level:
            h += 1
            level = [c for n in level for c in (n.left, n.right) if c is not self.NIL]
        return h

    def check(self):
        """Verify all Red-Black properties. Returns the black height."""
        if self.root.color != BLACK:
            raise AssertionError("root must be black")

        def walk(n, lo, hi):
            if n is self.NIL:
                return 1
            if n.color == RED and (n.left.color == RED or n.right.color == RED):
                raise AssertionError("red node has a red child")
            if (lo is not None and n.key <= lo) or (hi is not None and n.key >= hi):
                raise AssertionError("BST order violated")
            lh, rh = walk(n.left, lo, n.key), walk(n.right, n.key, hi)
            if lh != rh:
                raise AssertionError("black heights differ")
            return lh + (1 if n.color == BLACK else 0)

        return walk(self.root, None, None) - 1
