
inpu = """ A
 A
AA

 B
BB
BB

 C
 C
 C
CC

 D
 D
DD
 D

 E
 E
EE
E

F
FF

  G
  G
GGG

  H
 HH
HH

I I
III

J
J
J
J

KK
KK

 L
LLL
 L"""


class vector:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, v):
        return vector(self.x + v.x, self.y + v.y, self.z + v.z)

    def __sub__(self, v):
        return vector(self.x - v.x, self.y - v.y, self.z - v.z)


pfill = .8


class piece:
    def __init__(self, spots):
        self.pos = vector(0, 0, 0)
        self.spots = spots
        self.circs = []

    def get_spots(self):
        l = []
        for spot in self.spots:
            v = vector(spot[0], spot[1], 0)
            l.append(self.pos + v)
        return l

    def setpos(self, newpos):
        self.pos = vector(newpos[0], newpos[1], 0)

    def set_visible(self):
        for c in self.circs:
            c.opacity = 1

    def set_invisible(self):
        for c in self.circs:
            c.opacity = 0

    def insersects(self, other):
        for spot in self.get_spots():
            for spot2 in other.get_spots():
                if spot == spot2:
                    return True
        return False

    def touches(self, spot):
        v = vector(spot[0], spot[1], 0)
        for s in self.get_spots():
            if s == v:
                return True
        return False


class board:
    def __init__(self, posi, len, lon, w, h):
        self.w = w
        self.h = h
        self.dim = [len, lon]
        self.bools = [False] * (w * h)
        self.holes = []  # all the holes (just for visualization)
        self.pieces = []

    def get(self, i, j):
        if i < 0 or i >= self.w:
            return False
        if j < 0 or j >= self.h:
            return False
        return self.bools[i + j * self.w]

    def add_piece(self, p, pose=None):
        if pose is not None:
            p.setpos(pose)
        spots = p.get_spots()
        for spot in spots:
            if self.get(spot.x, spot.y):
                return False
        for spot in spots:
            self.bools[spot.x + spot.y * self.w] = True
        self.pieces.append(p)
        p.set_visible()

    def remove_last(self):
        for spot in self.pieces[-1].get_spots():
            self.bools[spot.x + spot.y * self.w] = False
        self.pieces[-1].set_invisible()
        self.pieces = self.pieces[:-1]

    def find_solution(self, pieces):
        poslook = self._find_empty()
        for piece in pieces:
            pass

    def _find_empty(self):
        for i in range(self.w):
            for j in range(self.h):
                if not self.get(i, j):
                    return (i, j)
        return None


class _node:

    def __init__(self, value=None, lchild=None, rchild=None, top=None):
        self._val = value
        self.left = lchild
        self.right = rchild
        self.top = top
        if self.left is None:
            self.left = self
        if self.right is None:
            self.right = self

    def val(self):
        return self._val

    def remove(self):
        self.left.right = self.right
        self.right.left = self.left

    def put_back(self):
        self.left.right = self
        self.right.left = self

    def __repr__(self):
        return 'node ' + str(self._val) + '\t l: ' + str(self.left.val()) + '\t r: ' + str(self.right.val())


# a value linked list, each node is expected to have a value of its index
# in some array its contained in
class vllist:

    def __init__(self, name):
        self._size = 0
        self._root = _node(value=name)
        self._end = self._root

    def val(self):
        return self._root.val()

    def __len__(self):
        return self._size

    def append(self, item=None, top=None):
        if top is None:
            top = self
        self._size += 1
        if self._root is None:
            self._root = _node(value=item, lchild=self, rchild=self, top=top)
            self._end = self._root
        else:
            self._end.right = _node(value=item, lchild=self._end, rchild=self._root, top=top)
            self._end = self._end.right
            self._root.left = self._end

    def remove(self, node):
        if node is None:
            return
        if self._root == node:
            raise RuntimeError('don\'t remove root node')
        self._size -= 1
        node.remove()
        if self._end == node:
            self._end = node.left

    def put_back(self, node):
        if node is None:
            return
        self._size += 1
        node.put_back()
        if self._end == node.left:
            self._end = node

    def get(self, item):
        i = self._root
        while i is not None:
            if i.val()== item:
                return i
            i = i.right
            if i == self._root:
                break
        return None

    def get_first(self):
        return self._root.right.val()

    def get_last(self):
        return self._end.val()

    def get_first_node(self):
        return self._root.right

    def get_last_node(self):
        return self._end

    class _reverseiter:

        def __init__(self, start, len):
            self._a = start
            self._count = 0
            self._len = len

        def __next__(self):
            if self._count == self._len:
                raise StopIteration
            self._count += 1
            ret = self._a
            self._a = self._a.left
            return ret

        def __repr__(self):
            if self._len == 0:
                return '[]'
            s = '['
            c = 0
            while c < self._len:
                c += 1
                s += str(self._a.val()) + ', '
                self.__next__()
            return s[:-2] + ']'

    def __reversed__(self):
        return self._reverseiter(self._end, len(self))

    def __iter__(self):
        self._start = self._root.right
        self._count = 0
        return self

    def __next__(self):
        if self._count == len(self):
            raise StopIteration
        self._count += 1
        ret = self._start
        self._start = self._start.right
        return ret

    def peek(self):
        return self._start

    def __repr__(self):
        return self._root.val()
        # if len(self) == 0:
        #     return '[]'
        # s = '['
        # for i in self:
        #     if i.val() is not None:
        #         s += str(i.val()) + ', '
        #     else:
        #         s += '_, '
        # return s[:-2] + ']'


class dancing_links:

    def __init__(self, opts_and_items, itemlist):
        # opts_and_items is a list of options which each contain
        # a list of items
        if not hasattr(opts_and_items, '__getitem__'):
            raise TypeError('first argument of constructor must define __getitem__ (random access)')
        self._array = []
        self._heads = vllist('heads') # list of all items
        lookup = {}
        count = 0
        for item in itemlist:
            lis = vllist(name=item)
            self._heads.append(lis)
            self._array.append(self._heads.get_last_node())
            lookup[item] = count
            count += 1

        count = 1
        # first marker for end of rows. Has no lchild, rchild will be set later
        self._array.append(_node(value=len(self._array), top=-count))
        last_marker = self._array[-1]
        for option in opts_and_items:
            first = None
            for item in option:
                index = lookup[item]
                # add the index of the spot in array
                self._array[index].val().append(len(self._array), top=index)
                self._array.append(self._array[index].val().get_last_node())
                if first is None:
                    first = self._array[-1]
            last = self._array[-1]
            last_marker.right = last

            count += 1
            # marker for the end of a row
            # top is negative (so we know its a marker for the end) and corresponds
            # to the negative of the index of the
            self._array.append(_node(value=len(self._array), lchild=first, top=-count))
            last_marker = self._array[-1]

        for item in self._array:
            print(item)

    def cover(self, attr_index):
        node = self._array[attr_index]
        for p in node.val():
            self.hide(p)
        self._heads.remove(node)

    def hide(self, node):
        p = node.val()
        q = p + 1
        while q != p:
            n = self._array[q]
            if n.top < 0: # node is a spacer
                q = n.left.val()
            else:
                self._array[n.top].remove(n)
                q += 1

    def uncover(self, attr_index):
        node = self._array[attr_index]
        node.put_back()
        for p in reversed(node.val()):
            self.unhide(p)

    def unhide(self, node):
        p = node.val()
        q = p - 1
        while q != p:
            n = self._array[q]
            if n.top < 0:
                q = n.right.val()
            else:
                self._array[n.top].put_back(n)
                q -= 1


b = board(vector(0, 0, -.25), 11, 5, 11, 5)

pieces = []

pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [3, 0])))
pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [3, 0], [0, 1])))
pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [0, 1])))
pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [0, 1], [0, 2])))
pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [0, 1], [1, 1])))
pieces.append(piece(spots=([1, 0], [0, 1], [1, 1], [2, 1], [1, 2])))
pieces.append(piece(spots=([0, 0], [1, 0], [1, 1], [2, 1], [2, 2])))
pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [2, 1], [3, 1])))
pieces.append(piece(spots=([0, 0], [1, 0], [1, 1])))
pieces.append(piece(spots=([0, 0], [1, 0], [0, 1], [1, 1])))
pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [0, 1], [2, 1])))
pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [3, 0], [2, 1])))

mom = vector(0, 0, 0)
t = 0
dt = .01

b.add_piece(pieces[2], pose=(0, 1))
b.add_piece(pieces[6], pose=(5, 2))


# l = vllist('list')
#
# l.append(1)
# l.append(3)
# l.append(2)
# l.append(4)
#
# l.remove(l.get_last_node())
# l.remove(l.get_first_node())
# l.remove(l.get_last_node())
#
# print(l)
# print(reversed(l))

d = dancing_links([['a', 'c'], ['b', 'c'], ['a']], ['a', 'b', 'c'])

