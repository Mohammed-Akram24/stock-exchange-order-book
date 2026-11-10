"""Binary Min-Heap written from scratch; used to expire orders on time. (Unit III)"""


class MinHeap:
    def __init__(self):
        self.a = []

    def __len__(self):
        return len(self.a)

    def peek(self):
        return self.a[0]

    def push(self, item):
        a = self.a
        a.append(item)
        i = len(a) - 1
        while i > 0 and a[(i - 1) // 2] > a[i]:
            a[(i - 1) // 2], a[i] = a[i], a[(i - 1) // 2]
            i = (i - 1) // 2

    def pop(self):
        a = self.a
        top, last = a[0], a.pop()
        if a:
            a[0] = last
            i, n = 0, len(a)
            while True:
                s, l, r = i, 2 * i + 1, 2 * i + 2
                if l < n and a[l] < a[s]:
                    s = l
                if r < n and a[r] < a[s]:
                    s = r
                if s == i:
                    break
                a[i], a[s] = a[s], a[i]
                i = s
        return top
