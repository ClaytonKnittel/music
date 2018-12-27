
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

    def __repr__(self):
        return '<' + str(self.x) + ', ' + str(self.y) + '>'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        r = 31
        r = 17 * r + self.x
        r = 17 * r + self.y
        return r


pfill = .8


class piece:

    # symmetry levels:
    #     0: no symmetries
    #     1: axial symmetry (only do first 2 orientations)
    #     2: biaxial symmetry (only flip)
    #     3: mirror image of itself (don't flip)
    #     4: axial and mirror symmetry (only do first 2 orientations and don't flip)
    #     5: entirely symmetric (don't do anything)
    def __init__(self, spots, x=0, y=0, orientation=0, flipped=False, symmetry_level=0):
        self.pos = vector(x, y, 0)
        self.spots = spots
        self.orientation = orientation
        self.flipped = flipped
        self.sym = symmetry_level

    def get_spots(self):
        l = []
        for spot in self.spots:
            dx = spot[0]
            dy = spot[1]
            if self.flipped:
                dy *= -1
            if self.orientation == 0:
                v = vector(dx, dy, 0)
            elif self.orientation == 1:
                v = vector(-dy, dx, 0)
            elif self.orientation == 2:
                v = vector(-dx, -dy, 0)
            else:
                v = vector(dy, -dx, 0)
            l.append(self.pos + v)
        return l

    def gen_all_spots(self, w, h):
        if self.sym % 3 == 2:
            ors = range(1)
        elif self.sym % 3 == 1:
            ors = range(2)
        else:
            ors = range(4)
        for orientation in ors:
            if self.sym >= 3:
                flips = [False]
            else:
                flips = [False, True]

            for flipped in flips:
                p = piece(self.spots, orientation=orientation, flipped=flipped)
                spots = list(p.get_spots())
                sx = -min(v.x for v in spots)
                sy = -min(v.y for v in spots)
                wid = w - max(v.x for v in spots)
                hei = h - max(v.y for v in spots)
                for x in range(sx, wid):
                    for y in range(sy, hei):
                        yield piece(p.spots, x, y, orientation=orientation, flipped=flipped).get_spots()

    def setpos(self, newpos):
        self.pos = vector(newpos[0], newpos[1], 0)

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
        all_pieces_and_orientations = []
        count = 0
        attrs = list('is ' + str(w) for w in range(len(pieces)))
        for x in range(self.w):
            for y in range(self.h):
                attrs += [vector(x, y, 0)]

        for piece in pieces:
            arad = ['is ' + str(count)]
            for spots in piece.gen_all_spots(self.w, self.h):
                all_pieces_and_orientations.append(arad + spots)
            count += 1
        d = dancing_links(all_pieces_and_orientations, attrs)
        for attr in attrs:
            print('attr', attr)
        for soln in d.solve():
            print('fup')
            print(soln)
            return
        print('done')


class _node:

    def __init__(self, name=None, value=None, lchild=None, rchild=None, top=None, len=None):
        if name is not None:
            self.name = str(name)
        else:
            self.name = None
        self._val = value
        self.left = lchild
        self.right = rchild
        self.top = top
        if self.left is None:
            self.left = self
        if self.right is None:
            self.right = self
        self._len = len

    def __len__(self):
        return self._len

    def dec(self):
        self._len -= 1

    def inc(self):
        self._len += 1

    def val(self):
        return self._val

    def remove(self):
        self.left.right = self.right
        self.right.left = self.left

    def put_back(self):
        self.left.right = self
        self.right.left = self

    def append(self, val, top=None):
        l = self.left
        self.left = _node(name='added by _node.append', value=val, lchild=l, rchild=self, top=top)
        l.right = self.left
        self._len += 1

    def get_last(self):
        return self.left

    def __repr__(self):
        if self.name is not None:
            return self.name
        return 'node ' + str(self._val) + '\t l: ' + str(self.left.val()) + '\t r: ' + str(self.right.val())\
               + '\t t: ' + str(self.top)


# a linked list backed by an array of nodes (for random access)
class allist:

    def __init__(self, name):
        self._size = 0
        self._root = _node(value=name)
        self._end = self._root
        self._ar = []

    def val(self):
        return self._root.val()

    def __len__(self):
        return self._size

    def inside(self, node):
        for n in self:
            if n == node:
                return True
        return False

    def append_node(self, node):
        self._size += 1
        self._end.right = node
        node.left = self._end
        node.right = self._root
        self._end = node
        self._root.left = self._end

        self._ar.append(self._end)

    def append(self, item=None, top=None):
        if top is None:
            top = self
        self.append_node(_node(name='added by allist.append', value=item, top=top))

    # remove from the llist, expecting it to be added back later (does not
    # remove from the array)
    def remove(self, node):
        if node == None:
            raise RuntimeError('don\'t remove NoneType')
        if self._root == node:
            raise RuntimeError('don\'t remove root node')
        self._size -= 1
        node.remove()
        if self._end == node:
            self._end = node.left

    def put_back(self, node):
        self._size += 1
        node.put_back()
        if self._end == node.left:
            self._end = node

    def get(self, item):
        return self._ar[item]

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

    def __repr__(self):
        if len(self) == 0:
            return '[]'
        s = '['
        for i in self:
            if i.val() is not None:
                s += str(i.val()) + ', '
            else:
                s += '_, '
        return s[:-2] + ']'


def printfm(dl, strr):
    boar = ['_'] * (5 * 11)
    label = '_'
    for r in strr.split('\n'):
        if r == '':
            continue
        if r[0] == 'i':
            label = r[3:]
            continue
        i, j = r[1:-1].split(', ')
        x = int(i)
        y = int(j)
        boar[x + 11 * y] = label
    for y in range(5):
        p = ''
        for x in range(11):
            v = vector(x, y, 0)
            l = dl._heads.get(dl.lookup[v])
            count = str(len(l.val()))
            if dl._heads.inside(l):
                ad = '+'
            else:
                ad = '!'
            lab = '[' + boar[x + 11 * y] + '] ' + ad + count
            p += lab + ' ' * (12 - len(lab))
        print(p)


class dancing_links:

    def __init__(self, opts_and_items, itemlist):
        # opts_and_items is a list of options which each contain
        # a list of items
        if not hasattr(opts_and_items, '__getitem__'):
            raise TypeError('first argument of constructor must define __getitem__ (random access)')
        self._array = []
        self._heads = allist('heads') # list of all items
        self._opts = {}
        self.lookup = {}
        count = 0
        for item in itemlist:
            self._array.append(_node(name=item, value=count, len=0))
            self._heads.append(self._array[-1])
            self.lookup[item] = count
            count += 1

        count = 1
        # first marker for end of rows. Has no lchild, rchild will be set later
        self._array.append(_node(value=len(self._array), top=-count))
        last_marker = self._array[-1]
        for option in opts_and_items:
            first = None
            for item in option:
                index = self.lookup[item]
                # add the index of the spot in array
                self._array[index].append(len(self._array), top=index)
                self._array.append(self._array[index].get_last())

                # so we can refer back to the options later when forming solutions
                self._opts[self._array[-1].val()] = option

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

    def print(self):
        for item in self._array:
            print(item)

    def print_pretty(self):
        size = 8
        off = -1
        while off < len(self._array):
            lok = self._array[max([off,0]):off+size]
            s = ''
            for i in lok:
                s += str(i.val() + 1) + '\t'
            print(s)
            s = ''
            for i in lok:
                if i.top is None:
                    s += 'N\t'
                else:
                    s += str(i.top + 1) + '\t'
            print(s)
            s = ''
            for i in lok:
                s += str(i.left.val() + 1) + '\t'
            print(s)
            s = ''
            for i in lok:
                s += str(i.right.val() + 1) + '\t'
            print(s)
            print()

            off += size

    def solve(self):
        self.solns = []
        self.solve_subprob([])
        return self.solns

    def solve_subprob(self, partial_soln):
        if len(self._heads) == 0:
            self.solns.append(partial_soln.copy())
            print(len(self.solns))
            # strr = ''
            # for s in self.solns[-1]:
            #     for q in s:
            #         strr += str(q) + '\n'
            # printfm(self, strr)
            return
        min = -1
        node = None
        for head in self._heads:
            l = len(head.val())
            if l < min or min == -1:
                min = l
                node = head
        if min == 0:
            return
        attr_index = self._heads._ar.index(node)
        self.try_attr(attr_index, partial_soln)

    def try_attr(self, attr_index, partial_soln):
        self.cover(attr_index)
        xl = self._array[attr_index].right.val()
        while xl != attr_index:
            self.try_cover(xl)
            self.solve_subprob(partial_soln + [xl])
            self.uncover_try(xl)
            xl = self._array[xl].right.val()
        self.uncover(attr_index)

    def try_cover(self, xl):
        p = xl + 1
        while p != xl:
            top = self._array[p].top
            if top < 0:
                p = self._array[p].left.val()
            else:
                self.cover(top)
                p += 1

    def uncover_try(self, xl):
        p = xl - 1
        while p != xl:
            top = self._array[p].top
            if top < 0:
                p = self._array[p].right.val()
            else:
                self.uncover(top)
                p -= 1

    def cover(self, attr_index):
        node = self._array[attr_index]
        p = node.right
        while p.val() != attr_index:
            self.hide(p)
            p = p.right
        self._heads.remove(self._heads.get(attr_index))

    def hide(self, node):
        p = node.val()
        q = p + 1
        while q != p:
            n = self._array[q]
            if n.top < 0: # node is a spacer
                q = n.left.val()
            else:
                n.remove()

                top = self._array[n.top]
                top.dec()
                # if len(top) == 0:
                #     self._heads.remove(top)
                q += 1

    def uncover(self, attr_index):
        self._heads.put_back(self._heads.get(attr_index))
        node = self._array[attr_index]
        p = node.left
        while p.val() != attr_index:
            self.unhide(p)
            p = p.left

    def unhide(self, node):
        p = node.val()
        q = p - 1
        while q != p:
            n = self._array[q]
            if n.top < 0:
                q = n.right.val()
            else:
                self._array[n.val()].put_back()

                top = self._array[n.top]
                top.inc()
                # if len(top) == 1:
                #     self._heads.put_back(top)
                q -= 1


b = board(vector(0, 0, -.25), 11, 5, 11, 5)

pieces = []

# symmetry levels:
#     0: no symmetries
#     1: axial symmetry (only do first 2 orientations)
#     2: biaxial symmetry (only flip)
#     3: mirror image of itself (don't flip)
#     4: axial and mirror symmetry (only do first 2 orientations and don't flip)
#     5: entirely symmetric (don't do anything)

pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [3, 0]), symmetry_level=4))
pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [3, 0], [0, 1]), symmetry_level=0))
pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [0, 1]), symmetry_level=3))
pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [0, 1], [0, 2]), symmetry_level=3))
pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [0, 1], [1, 1]), symmetry_level=0))
pieces.append(piece(spots=([1, 0], [0, 1], [1, 1], [2, 1], [1, 2]), symmetry_level=5))
pieces.append(piece(spots=([0, 0], [1, 0], [1, 1], [2, 1], [2, 2]), symmetry_level=3))
pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [2, 1], [3, 1]), symmetry_level=0))
pieces.append(piece(spots=([0, 0], [1, 0], [1, 1]), symmetry_level=3))
pieces.append(piece(spots=([0, 0], [1, 0], [0, 1], [1, 1]), symmetry_level=5))
pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [0, 1], [2, 1]), symmetry_level=3))
pieces.append(piece(spots=([0, 0], [1, 0], [2, 0], [3, 0], [2, 1]), symmetry_level=0))


b.find_solution(pieces)


o = """is 0
<0, 0>
<1, 0>
<2, 0>
<3, 0>
is 1
<0, 1>
<1, 1>
<2, 1>
<3, 1>
<0, 2>
is 2
<1, 2>
<2, 2>
<3, 2>
<1, 3>
is 3
<4, 0>
<5, 0>
<6, 0>
<4, 1>
<4, 2>
is 4
<2, 4>
<3, 4>
<4, 4>
<2, 3>
<3, 3>
is 5
<5, 2>
<4, 3>
<5, 3>
<6, 3>
<5, 4>
is 6
<8, 2>
<8, 1>
<9, 1>
<9, 0>
<10, 0>
is 7
<5, 1>
<6, 1>
<7, 1>
<7, 0>
<8, 0>
is 8
<1, 4>
<0, 4>
<0, 3>
is 9
<8, 3>
<9, 3>
<8, 4>
<9, 4>
is 10
<7, 2>
<7, 3>
<7, 4>
<6, 2>
<6, 4>
is 11
<10, 4>
<10, 3>
<10, 2>
<10, 1>
<9, 2>"""

# d = dancing_links([['c', 'e'], ['a', 'd', 'g'], ['b', 'c', 'f'], ['a', 'd', 'f'], ['b', 'g'], ['d', 'e', 'g']],
#                   ['a', 'b', 'c', 'd', 'e', 'f', 'g'])

# d = dancing_links([['a'], ['b']], ['a', 'b'])

# print(d.solve())
