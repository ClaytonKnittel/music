
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

    def quickstr(self):
        return str(self.x) + ',' + str(self.y)

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

    def write_permutations(self, pieces, file_loc):
        all_pieces_and_orientations = []
        count = 0
        attrs = list(w for w in range(len(pieces)))
        for x in range(self.w):
            for y in range(self.h):
                attrs += [vector(x, y, 0)]

        for piece in pieces:
            arad = [count]
            for spots in piece.gen_all_spots(self.w, self.h):
                all_pieces_and_orientations.append(arad + spots)
            count += 1
        total = ''
        for w in range(len(pieces)):
            total += 'w' + str(w) + ' '
        for i in range(11):
            for j in range(5):
                total += vector(i, j, 0).quickstr() + ' '
        total = total[:-1] + '\n'
        for p in all_pieces_and_orientations:
            s = 'w' + str(p[0])
            for pp in p[1:]:
                s += ' ' + pp.quickstr()
            print(s)
            total += s + '\n'
        total = total[:-1]
        f = open(file_loc, 'w')
        f.write(total)
        f.close()
        # d = dancing_links(all_pieces_and_orientations, attrs)
        # d.solve()


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
            #print(head)
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


# b.write_permutations(pieces, 'kan.txt')


# d = dancing_links([['c', 'e'], ['a', 'd', 'g'], ['b', 'c', 'f'], ['a', 'd', 'f'], ['b', 'g'], ['d', 'e', 'g']],
#                   ['a', 'b', 'c', 'd', 'e', 'f', 'g'])

# d = dancing_links([['a'], ['b']], ['a', 'b'])

# print(d.solve())


st = """w0 w1 w2 w3 w4 w5 w6 w7 w8 w9 w10 w11 0,0 0,1 0,2 0,3 0,4 1,0 1,1 1,2 1,3 1,4 2,0 2,1 2,2 2,3 2,4 3,0 3,1 3,2 3,3 3,4 4,0 4,1 4,2 4,3 4,4 5,0 5,1 5,2 5,3 5,4 6,0 6,1 6,2 6,3 6,4 7,0 7,1 7,2 7,3 7,4 8,0 8,1 8,2 8,3 8,4 9,0 9,1 9,2 9,3 9,4 10,0 10,1 10,2 10,3 10,4
w0 0,0 1,0 2,0 3,0
w0 0,1 1,1 2,1 3,1
w0 0,2 1,2 2,2 3,2
w0 0,3 1,3 2,3 3,3
w0 0,4 1,4 2,4 3,4
w0 1,0 2,0 3,0 4,0
w0 1,1 2,1 3,1 4,1
w0 1,2 2,2 3,2 4,2
w0 1,3 2,3 3,3 4,3
w0 1,4 2,4 3,4 4,4
w0 2,0 3,0 4,0 5,0
w0 2,1 3,1 4,1 5,1
w0 2,2 3,2 4,2 5,2
w0 2,3 3,3 4,3 5,3
w0 2,4 3,4 4,4 5,4
w0 3,0 4,0 5,0 6,0
w0 3,1 4,1 5,1 6,1
w0 3,2 4,2 5,2 6,2
w0 3,3 4,3 5,3 6,3
w0 3,4 4,4 5,4 6,4
w0 4,0 5,0 6,0 7,0
w0 4,1 5,1 6,1 7,1
w0 4,2 5,2 6,2 7,2
w0 4,3 5,3 6,3 7,3
w0 4,4 5,4 6,4 7,4
w0 5,0 6,0 7,0 8,0
w0 5,1 6,1 7,1 8,1
w0 5,2 6,2 7,2 8,2
w0 5,3 6,3 7,3 8,3
w0 5,4 6,4 7,4 8,4
w0 6,0 7,0 8,0 9,0
w0 6,1 7,1 8,1 9,1
w0 6,2 7,2 8,2 9,2
w0 6,3 7,3 8,3 9,3
w0 6,4 7,4 8,4 9,4
w0 7,0 8,0 9,0 10,0
w0 7,1 8,1 9,1 10,1
w0 7,2 8,2 9,2 10,2
w0 7,3 8,3 9,3 10,3
w0 7,4 8,4 9,4 10,4
w0 0,0 0,1 0,2 0,3
w0 0,1 0,2 0,3 0,4
w0 1,0 1,1 1,2 1,3
w0 1,1 1,2 1,3 1,4
w0 2,0 2,1 2,2 2,3
w0 2,1 2,2 2,3 2,4
w0 3,0 3,1 3,2 3,3
w0 3,1 3,2 3,3 3,4
w0 4,0 4,1 4,2 4,3
w0 4,1 4,2 4,3 4,4
w0 5,0 5,1 5,2 5,3
w0 5,1 5,2 5,3 5,4
w0 6,0 6,1 6,2 6,3
w0 6,1 6,2 6,3 6,4
w0 7,0 7,1 7,2 7,3
w0 7,1 7,2 7,3 7,4
w0 8,0 8,1 8,2 8,3
w0 8,1 8,2 8,3 8,4
w0 9,0 9,1 9,2 9,3
w0 9,1 9,2 9,3 9,4
w0 10,0 10,1 10,2 10,3
w0 10,1 10,2 10,3 10,4
w1 0,0 1,0 2,0 3,0 0,1
w1 0,1 1,1 2,1 3,1 0,2
w1 0,2 1,2 2,2 3,2 0,3
w1 0,3 1,3 2,3 3,3 0,4
w1 1,0 2,0 3,0 4,0 1,1
w1 1,1 2,1 3,1 4,1 1,2
w1 1,2 2,2 3,2 4,2 1,3
w1 1,3 2,3 3,3 4,3 1,4
w1 2,0 3,0 4,0 5,0 2,1
w1 2,1 3,1 4,1 5,1 2,2
w1 2,2 3,2 4,2 5,2 2,3
w1 2,3 3,3 4,3 5,3 2,4
w1 3,0 4,0 5,0 6,0 3,1
w1 3,1 4,1 5,1 6,1 3,2
w1 3,2 4,2 5,2 6,2 3,3
w1 3,3 4,3 5,3 6,3 3,4
w1 4,0 5,0 6,0 7,0 4,1
w1 4,1 5,1 6,1 7,1 4,2
w1 4,2 5,2 6,2 7,2 4,3
w1 4,3 5,3 6,3 7,3 4,4
w1 5,0 6,0 7,0 8,0 5,1
w1 5,1 6,1 7,1 8,1 5,2
w1 5,2 6,2 7,2 8,2 5,3
w1 5,3 6,3 7,3 8,3 5,4
w1 6,0 7,0 8,0 9,0 6,1
w1 6,1 7,1 8,1 9,1 6,2
w1 6,2 7,2 8,2 9,2 6,3
w1 6,3 7,3 8,3 9,3 6,4
w1 7,0 8,0 9,0 10,0 7,1
w1 7,1 8,1 9,1 10,1 7,2
w1 7,2 8,2 9,2 10,2 7,3
w1 7,3 8,3 9,3 10,3 7,4
w1 0,1 1,1 2,1 3,1 0,0
w1 0,2 1,2 2,2 3,2 0,1
w1 0,3 1,3 2,3 3,3 0,2
w1 0,4 1,4 2,4 3,4 0,3
w1 1,1 2,1 3,1 4,1 1,0
w1 1,2 2,2 3,2 4,2 1,1
w1 1,3 2,3 3,3 4,3 1,2
w1 1,4 2,4 3,4 4,4 1,3
w1 2,1 3,1 4,1 5,1 2,0
w1 2,2 3,2 4,2 5,2 2,1
w1 2,3 3,3 4,3 5,3 2,2
w1 2,4 3,4 4,4 5,4 2,3
w1 3,1 4,1 5,1 6,1 3,0
w1 3,2 4,2 5,2 6,2 3,1
w1 3,3 4,3 5,3 6,3 3,2
w1 3,4 4,4 5,4 6,4 3,3
w1 4,1 5,1 6,1 7,1 4,0
w1 4,2 5,2 6,2 7,2 4,1
w1 4,3 5,3 6,3 7,3 4,2
w1 4,4 5,4 6,4 7,4 4,3
w1 5,1 6,1 7,1 8,1 5,0
w1 5,2 6,2 7,2 8,2 5,1
w1 5,3 6,3 7,3 8,3 5,2
w1 5,4 6,4 7,4 8,4 5,3
w1 6,1 7,1 8,1 9,1 6,0
w1 6,2 7,2 8,2 9,2 6,1
w1 6,3 7,3 8,3 9,3 6,2
w1 6,4 7,4 8,4 9,4 6,3
w1 7,1 8,1 9,1 10,1 7,0
w1 7,2 8,2 9,2 10,2 7,1
w1 7,3 8,3 9,3 10,3 7,2
w1 7,4 8,4 9,4 10,4 7,3
w1 1,0 1,1 1,2 1,3 0,0
w1 1,1 1,2 1,3 1,4 0,1
w1 2,0 2,1 2,2 2,3 1,0
w1 2,1 2,2 2,3 2,4 1,1
w1 3,0 3,1 3,2 3,3 2,0
w1 3,1 3,2 3,3 3,4 2,1
w1 4,0 4,1 4,2 4,3 3,0
w1 4,1 4,2 4,3 4,4 3,1
w1 5,0 5,1 5,2 5,3 4,0
w1 5,1 5,2 5,3 5,4 4,1
w1 6,0 6,1 6,2 6,3 5,0
w1 6,1 6,2 6,3 6,4 5,1
w1 7,0 7,1 7,2 7,3 6,0
w1 7,1 7,2 7,3 7,4 6,1
w1 8,0 8,1 8,2 8,3 7,0
w1 8,1 8,2 8,3 8,4 7,1
w1 9,0 9,1 9,2 9,3 8,0
w1 9,1 9,2 9,3 9,4 8,1
w1 10,0 10,1 10,2 10,3 9,0
w1 10,1 10,2 10,3 10,4 9,1
w1 0,0 0,1 0,2 0,3 1,0
w1 0,1 0,2 0,3 0,4 1,1
w1 1,0 1,1 1,2 1,3 2,0
w1 1,1 1,2 1,3 1,4 2,1
w1 2,0 2,1 2,2 2,3 3,0
w1 2,1 2,2 2,3 2,4 3,1
w1 3,0 3,1 3,2 3,3 4,0
w1 3,1 3,2 3,3 3,4 4,1
w1 4,0 4,1 4,2 4,3 5,0
w1 4,1 4,2 4,3 4,4 5,1
w1 5,0 5,1 5,2 5,3 6,0
w1 5,1 5,2 5,3 5,4 6,1
w1 6,0 6,1 6,2 6,3 7,0
w1 6,1 6,2 6,3 6,4 7,1
w1 7,0 7,1 7,2 7,3 8,0
w1 7,1 7,2 7,3 7,4 8,1
w1 8,0 8,1 8,2 8,3 9,0
w1 8,1 8,2 8,3 8,4 9,1
w1 9,0 9,1 9,2 9,3 10,0
w1 9,1 9,2 9,3 9,4 10,1
w1 3,1 2,1 1,1 0,1 3,0
w1 3,2 2,2 1,2 0,2 3,1
w1 3,3 2,3 1,3 0,3 3,2
w1 3,4 2,4 1,4 0,4 3,3
w1 4,1 3,1 2,1 1,1 4,0
w1 4,2 3,2 2,2 1,2 4,1
w1 4,3 3,3 2,3 1,3 4,2
w1 4,4 3,4 2,4 1,4 4,3
w1 5,1 4,1 3,1 2,1 5,0
w1 5,2 4,2 3,2 2,2 5,1
w1 5,3 4,3 3,3 2,3 5,2
w1 5,4 4,4 3,4 2,4 5,3
w1 6,1 5,1 4,1 3,1 6,0
w1 6,2 5,2 4,2 3,2 6,1
w1 6,3 5,3 4,3 3,3 6,2
w1 6,4 5,4 4,4 3,4 6,3
w1 7,1 6,1 5,1 4,1 7,0
w1 7,2 6,2 5,2 4,2 7,1
w1 7,3 6,3 5,3 4,3 7,2
w1 7,4 6,4 5,4 4,4 7,3
w1 8,1 7,1 6,1 5,1 8,0
w1 8,2 7,2 6,2 5,2 8,1
w1 8,3 7,3 6,3 5,3 8,2
w1 8,4 7,4 6,4 5,4 8,3
w1 9,1 8,1 7,1 6,1 9,0
w1 9,2 8,2 7,2 6,2 9,1
w1 9,3 8,3 7,3 6,3 9,2
w1 9,4 8,4 7,4 6,4 9,3
w1 10,1 9,1 8,1 7,1 10,0
w1 10,2 9,2 8,2 7,2 10,1
w1 10,3 9,3 8,3 7,3 10,2
w1 10,4 9,4 8,4 7,4 10,3
w1 3,0 2,0 1,0 0,0 3,1
w1 3,1 2,1 1,1 0,1 3,2
w1 3,2 2,2 1,2 0,2 3,3
w1 3,3 2,3 1,3 0,3 3,4
w1 4,0 3,0 2,0 1,0 4,1
w1 4,1 3,1 2,1 1,1 4,2
w1 4,2 3,2 2,2 1,2 4,3
w1 4,3 3,3 2,3 1,3 4,4
w1 5,0 4,0 3,0 2,0 5,1
w1 5,1 4,1 3,1 2,1 5,2
w1 5,2 4,2 3,2 2,2 5,3
w1 5,3 4,3 3,3 2,3 5,4
w1 6,0 5,0 4,0 3,0 6,1
w1 6,1 5,1 4,1 3,1 6,2
w1 6,2 5,2 4,2 3,2 6,3
w1 6,3 5,3 4,3 3,3 6,4
w1 7,0 6,0 5,0 4,0 7,1
w1 7,1 6,1 5,1 4,1 7,2
w1 7,2 6,2 5,2 4,2 7,3
w1 7,3 6,3 5,3 4,3 7,4
w1 8,0 7,0 6,0 5,0 8,1
w1 8,1 7,1 6,1 5,1 8,2
w1 8,2 7,2 6,2 5,2 8,3
w1 8,3 7,3 6,3 5,3 8,4
w1 9,0 8,0 7,0 6,0 9,1
w1 9,1 8,1 7,1 6,1 9,2
w1 9,2 8,2 7,2 6,2 9,3
w1 9,3 8,3 7,3 6,3 9,4
w1 10,0 9,0 8,0 7,0 10,1
w1 10,1 9,1 8,1 7,1 10,2
w1 10,2 9,2 8,2 7,2 10,3
w1 10,3 9,3 8,3 7,3 10,4
w1 0,3 0,2 0,1 0,0 1,3
w1 0,4 0,3 0,2 0,1 1,4
w1 1,3 1,2 1,1 1,0 2,3
w1 1,4 1,3 1,2 1,1 2,4
w1 2,3 2,2 2,1 2,0 3,3
w1 2,4 2,3 2,2 2,1 3,4
w1 3,3 3,2 3,1 3,0 4,3
w1 3,4 3,3 3,2 3,1 4,4
w1 4,3 4,2 4,1 4,0 5,3
w1 4,4 4,3 4,2 4,1 5,4
w1 5,3 5,2 5,1 5,0 6,3
w1 5,4 5,3 5,2 5,1 6,4
w1 6,3 6,2 6,1 6,0 7,3
w1 6,4 6,3 6,2 6,1 7,4
w1 7,3 7,2 7,1 7,0 8,3
w1 7,4 7,3 7,2 7,1 8,4
w1 8,3 8,2 8,1 8,0 9,3
w1 8,4 8,3 8,2 8,1 9,4
w1 9,3 9,2 9,1 9,0 10,3
w1 9,4 9,3 9,2 9,1 10,4
w1 1,3 1,2 1,1 1,0 0,3
w1 1,4 1,3 1,2 1,1 0,4
w1 2,3 2,2 2,1 2,0 1,3
w1 2,4 2,3 2,2 2,1 1,4
w1 3,3 3,2 3,1 3,0 2,3
w1 3,4 3,3 3,2 3,1 2,4
w1 4,3 4,2 4,1 4,0 3,3
w1 4,4 4,3 4,2 4,1 3,4
w1 5,3 5,2 5,1 5,0 4,3
w1 5,4 5,3 5,2 5,1 4,4
w1 6,3 6,2 6,1 6,0 5,3
w1 6,4 6,3 6,2 6,1 5,4
w1 7,3 7,2 7,1 7,0 6,3
w1 7,4 7,3 7,2 7,1 6,4
w1 8,3 8,2 8,1 8,0 7,3
w1 8,4 8,3 8,2 8,1 7,4
w1 9,3 9,2 9,1 9,0 8,3
w1 9,4 9,3 9,2 9,1 8,4
w1 10,3 10,2 10,1 10,0 9,3
w1 10,4 10,3 10,2 10,1 9,4
w2 0,0 1,0 2,0 0,1
w2 0,1 1,1 2,1 0,2
w2 0,2 1,2 2,2 0,3
w2 0,3 1,3 2,3 0,4
w2 1,0 2,0 3,0 1,1
w2 1,1 2,1 3,1 1,2
w2 1,2 2,2 3,2 1,3
w2 1,3 2,3 3,3 1,4
w2 2,0 3,0 4,0 2,1
w2 2,1 3,1 4,1 2,2
w2 2,2 3,2 4,2 2,3
w2 2,3 3,3 4,3 2,4
w2 3,0 4,0 5,0 3,1
w2 3,1 4,1 5,1 3,2
w2 3,2 4,2 5,2 3,3
w2 3,3 4,3 5,3 3,4
w2 4,0 5,0 6,0 4,1
w2 4,1 5,1 6,1 4,2
w2 4,2 5,2 6,2 4,3
w2 4,3 5,3 6,3 4,4
w2 5,0 6,0 7,0 5,1
w2 5,1 6,1 7,1 5,2
w2 5,2 6,2 7,2 5,3
w2 5,3 6,3 7,3 5,4
w2 6,0 7,0 8,0 6,1
w2 6,1 7,1 8,1 6,2
w2 6,2 7,2 8,2 6,3
w2 6,3 7,3 8,3 6,4
w2 7,0 8,0 9,0 7,1
w2 7,1 8,1 9,1 7,2
w2 7,2 8,2 9,2 7,3
w2 7,3 8,3 9,3 7,4
w2 8,0 9,0 10,0 8,1
w2 8,1 9,1 10,1 8,2
w2 8,2 9,2 10,2 8,3
w2 8,3 9,3 10,3 8,4
w2 1,0 1,1 1,2 0,0
w2 1,1 1,2 1,3 0,1
w2 1,2 1,3 1,4 0,2
w2 2,0 2,1 2,2 1,0
w2 2,1 2,2 2,3 1,1
w2 2,2 2,3 2,4 1,2
w2 3,0 3,1 3,2 2,0
w2 3,1 3,2 3,3 2,1
w2 3,2 3,3 3,4 2,2
w2 4,0 4,1 4,2 3,0
w2 4,1 4,2 4,3 3,1
w2 4,2 4,3 4,4 3,2
w2 5,0 5,1 5,2 4,0
w2 5,1 5,2 5,3 4,1
w2 5,2 5,3 5,4 4,2
w2 6,0 6,1 6,2 5,0
w2 6,1 6,2 6,3 5,1
w2 6,2 6,3 6,4 5,2
w2 7,0 7,1 7,2 6,0
w2 7,1 7,2 7,3 6,1
w2 7,2 7,3 7,4 6,2
w2 8,0 8,1 8,2 7,0
w2 8,1 8,2 8,3 7,1
w2 8,2 8,3 8,4 7,2
w2 9,0 9,1 9,2 8,0
w2 9,1 9,2 9,3 8,1
w2 9,2 9,3 9,4 8,2
w2 10,0 10,1 10,2 9,0
w2 10,1 10,2 10,3 9,1
w2 10,2 10,3 10,4 9,2
w2 2,1 1,1 0,1 2,0
w2 2,2 1,2 0,2 2,1
w2 2,3 1,3 0,3 2,2
w2 2,4 1,4 0,4 2,3
w2 3,1 2,1 1,1 3,0
w2 3,2 2,2 1,2 3,1
w2 3,3 2,3 1,3 3,2
w2 3,4 2,4 1,4 3,3
w2 4,1 3,1 2,1 4,0
w2 4,2 3,2 2,2 4,1
w2 4,3 3,3 2,3 4,2
w2 4,4 3,4 2,4 4,3
w2 5,1 4,1 3,1 5,0
w2 5,2 4,2 3,2 5,1
w2 5,3 4,3 3,3 5,2
w2 5,4 4,4 3,4 5,3
w2 6,1 5,1 4,1 6,0
w2 6,2 5,2 4,2 6,1
w2 6,3 5,3 4,3 6,2
w2 6,4 5,4 4,4 6,3
w2 7,1 6,1 5,1 7,0
w2 7,2 6,2 5,2 7,1
w2 7,3 6,3 5,3 7,2
w2 7,4 6,4 5,4 7,3
w2 8,1 7,1 6,1 8,0
w2 8,2 7,2 6,2 8,1
w2 8,3 7,3 6,3 8,2
w2 8,4 7,4 6,4 8,3
w2 9,1 8,1 7,1 9,0
w2 9,2 8,2 7,2 9,1
w2 9,3 8,3 7,3 9,2
w2 9,4 8,4 7,4 9,3
w2 10,1 9,1 8,1 10,0
w2 10,2 9,2 8,2 10,1
w2 10,3 9,3 8,3 10,2
w2 10,4 9,4 8,4 10,3
w2 0,2 0,1 0,0 1,2
w2 0,3 0,2 0,1 1,3
w2 0,4 0,3 0,2 1,4
w2 1,2 1,1 1,0 2,2
w2 1,3 1,2 1,1 2,3
w2 1,4 1,3 1,2 2,4
w2 2,2 2,1 2,0 3,2
w2 2,3 2,2 2,1 3,3
w2 2,4 2,3 2,2 3,4
w2 3,2 3,1 3,0 4,2
w2 3,3 3,2 3,1 4,3
w2 3,4 3,3 3,2 4,4
w2 4,2 4,1 4,0 5,2
w2 4,3 4,2 4,1 5,3
w2 4,4 4,3 4,2 5,4
w2 5,2 5,1 5,0 6,2
w2 5,3 5,2 5,1 6,3
w2 5,4 5,3 5,2 6,4
w2 6,2 6,1 6,0 7,2
w2 6,3 6,2 6,1 7,3
w2 6,4 6,3 6,2 7,4
w2 7,2 7,1 7,0 8,2
w2 7,3 7,2 7,1 8,3
w2 7,4 7,3 7,2 8,4
w2 8,2 8,1 8,0 9,2
w2 8,3 8,2 8,1 9,3
w2 8,4 8,3 8,2 9,4
w2 9,2 9,1 9,0 10,2
w2 9,3 9,2 9,1 10,3
w2 9,4 9,3 9,2 10,4
w3 0,0 1,0 2,0 0,1 0,2
w3 0,1 1,1 2,1 0,2 0,3
w3 0,2 1,2 2,2 0,3 0,4
w3 1,0 2,0 3,0 1,1 1,2
w3 1,1 2,1 3,1 1,2 1,3
w3 1,2 2,2 3,2 1,3 1,4
w3 2,0 3,0 4,0 2,1 2,2
w3 2,1 3,1 4,1 2,2 2,3
w3 2,2 3,2 4,2 2,3 2,4
w3 3,0 4,0 5,0 3,1 3,2
w3 3,1 4,1 5,1 3,2 3,3
w3 3,2 4,2 5,2 3,3 3,4
w3 4,0 5,0 6,0 4,1 4,2
w3 4,1 5,1 6,1 4,2 4,3
w3 4,2 5,2 6,2 4,3 4,4
w3 5,0 6,0 7,0 5,1 5,2
w3 5,1 6,1 7,1 5,2 5,3
w3 5,2 6,2 7,2 5,3 5,4
w3 6,0 7,0 8,0 6,1 6,2
w3 6,1 7,1 8,1 6,2 6,3
w3 6,2 7,2 8,2 6,3 6,4
w3 7,0 8,0 9,0 7,1 7,2
w3 7,1 8,1 9,1 7,2 7,3
w3 7,2 8,2 9,2 7,3 7,4
w3 8,0 9,0 10,0 8,1 8,2
w3 8,1 9,1 10,1 8,2 8,3
w3 8,2 9,2 10,2 8,3 8,4
w3 2,0 2,1 2,2 1,0 0,0
w3 2,1 2,2 2,3 1,1 0,1
w3 2,2 2,3 2,4 1,2 0,2
w3 3,0 3,1 3,2 2,0 1,0
w3 3,1 3,2 3,3 2,1 1,1
w3 3,2 3,3 3,4 2,2 1,2
w3 4,0 4,1 4,2 3,0 2,0
w3 4,1 4,2 4,3 3,1 2,1
w3 4,2 4,3 4,4 3,2 2,2
w3 5,0 5,1 5,2 4,0 3,0
w3 5,1 5,2 5,3 4,1 3,1
w3 5,2 5,3 5,4 4,2 3,2
w3 6,0 6,1 6,2 5,0 4,0
w3 6,1 6,2 6,3 5,1 4,1
w3 6,2 6,3 6,4 5,2 4,2
w3 7,0 7,1 7,2 6,0 5,0
w3 7,1 7,2 7,3 6,1 5,1
w3 7,2 7,3 7,4 6,2 5,2
w3 8,0 8,1 8,2 7,0 6,0
w3 8,1 8,2 8,3 7,1 6,1
w3 8,2 8,3 8,4 7,2 6,2
w3 9,0 9,1 9,2 8,0 7,0
w3 9,1 9,2 9,3 8,1 7,1
w3 9,2 9,3 9,4 8,2 7,2
w3 10,0 10,1 10,2 9,0 8,0
w3 10,1 10,2 10,3 9,1 8,1
w3 10,2 10,3 10,4 9,2 8,2
w3 2,2 1,2 0,2 2,1 2,0
w3 2,3 1,3 0,3 2,2 2,1
w3 2,4 1,4 0,4 2,3 2,2
w3 3,2 2,2 1,2 3,1 3,0
w3 3,3 2,3 1,3 3,2 3,1
w3 3,4 2,4 1,4 3,3 3,2
w3 4,2 3,2 2,2 4,1 4,0
w3 4,3 3,3 2,3 4,2 4,1
w3 4,4 3,4 2,4 4,3 4,2
w3 5,2 4,2 3,2 5,1 5,0
w3 5,3 4,3 3,3 5,2 5,1
w3 5,4 4,4 3,4 5,3 5,2
w3 6,2 5,2 4,2 6,1 6,0
w3 6,3 5,3 4,3 6,2 6,1
w3 6,4 5,4 4,4 6,3 6,2
w3 7,2 6,2 5,2 7,1 7,0
w3 7,3 6,3 5,3 7,2 7,1
w3 7,4 6,4 5,4 7,3 7,2
w3 8,2 7,2 6,2 8,1 8,0
w3 8,3 7,3 6,3 8,2 8,1
w3 8,4 7,4 6,4 8,3 8,2
w3 9,2 8,2 7,2 9,1 9,0
w3 9,3 8,3 7,3 9,2 9,1
w3 9,4 8,4 7,4 9,3 9,2
w3 10,2 9,2 8,2 10,1 10,0
w3 10,3 9,3 8,3 10,2 10,1
w3 10,4 9,4 8,4 10,3 10,2
w3 0,2 0,1 0,0 1,2 2,2
w3 0,3 0,2 0,1 1,3 2,3
w3 0,4 0,3 0,2 1,4 2,4
w3 1,2 1,1 1,0 2,2 3,2
w3 1,3 1,2 1,1 2,3 3,3
w3 1,4 1,3 1,2 2,4 3,4
w3 2,2 2,1 2,0 3,2 4,2
w3 2,3 2,2 2,1 3,3 4,3
w3 2,4 2,3 2,2 3,4 4,4
w3 3,2 3,1 3,0 4,2 5,2
w3 3,3 3,2 3,1 4,3 5,3
w3 3,4 3,3 3,2 4,4 5,4
w3 4,2 4,1 4,0 5,2 6,2
w3 4,3 4,2 4,1 5,3 6,3
w3 4,4 4,3 4,2 5,4 6,4
w3 5,2 5,1 5,0 6,2 7,2
w3 5,3 5,2 5,1 6,3 7,3
w3 5,4 5,3 5,2 6,4 7,4
w3 6,2 6,1 6,0 7,2 8,2
w3 6,3 6,2 6,1 7,3 8,3
w3 6,4 6,3 6,2 7,4 8,4
w3 7,2 7,1 7,0 8,2 9,2
w3 7,3 7,2 7,1 8,3 9,3
w3 7,4 7,3 7,2 8,4 9,4
w3 8,2 8,1 8,0 9,2 10,2
w3 8,3 8,2 8,1 9,3 10,3
w3 8,4 8,3 8,2 9,4 10,4
w4 0,0 1,0 2,0 0,1 1,1
w4 0,1 1,1 2,1 0,2 1,2
w4 0,2 1,2 2,2 0,3 1,3
w4 0,3 1,3 2,3 0,4 1,4
w4 1,0 2,0 3,0 1,1 2,1
w4 1,1 2,1 3,1 1,2 2,2
w4 1,2 2,2 3,2 1,3 2,3
w4 1,3 2,3 3,3 1,4 2,4
w4 2,0 3,0 4,0 2,1 3,1
w4 2,1 3,1 4,1 2,2 3,2
w4 2,2 3,2 4,2 2,3 3,3
w4 2,3 3,3 4,3 2,4 3,4
w4 3,0 4,0 5,0 3,1 4,1
w4 3,1 4,1 5,1 3,2 4,2
w4 3,2 4,2 5,2 3,3 4,3
w4 3,3 4,3 5,3 3,4 4,4
w4 4,0 5,0 6,0 4,1 5,1
w4 4,1 5,1 6,1 4,2 5,2
w4 4,2 5,2 6,2 4,3 5,3
w4 4,3 5,3 6,3 4,4 5,4
w4 5,0 6,0 7,0 5,1 6,1
w4 5,1 6,1 7,1 5,2 6,2
w4 5,2 6,2 7,2 5,3 6,3
w4 5,3 6,3 7,3 5,4 6,4
w4 6,0 7,0 8,0 6,1 7,1
w4 6,1 7,1 8,1 6,2 7,2
w4 6,2 7,2 8,2 6,3 7,3
w4 6,3 7,3 8,3 6,4 7,4
w4 7,0 8,0 9,0 7,1 8,1
w4 7,1 8,1 9,1 7,2 8,2
w4 7,2 8,2 9,2 7,3 8,3
w4 7,3 8,3 9,3 7,4 8,4
w4 8,0 9,0 10,0 8,1 9,1
w4 8,1 9,1 10,1 8,2 9,2
w4 8,2 9,2 10,2 8,3 9,3
w4 8,3 9,3 10,3 8,4 9,4
w4 0,1 1,1 2,1 0,0 1,0
w4 0,2 1,2 2,2 0,1 1,1
w4 0,3 1,3 2,3 0,2 1,2
w4 0,4 1,4 2,4 0,3 1,3
w4 1,1 2,1 3,1 1,0 2,0
w4 1,2 2,2 3,2 1,1 2,1
w4 1,3 2,3 3,3 1,2 2,2
w4 1,4 2,4 3,4 1,3 2,3
w4 2,1 3,1 4,1 2,0 3,0
w4 2,2 3,2 4,2 2,1 3,1
w4 2,3 3,3 4,3 2,2 3,2
w4 2,4 3,4 4,4 2,3 3,3
w4 3,1 4,1 5,1 3,0 4,0
w4 3,2 4,2 5,2 3,1 4,1
w4 3,3 4,3 5,3 3,2 4,2
w4 3,4 4,4 5,4 3,3 4,3
w4 4,1 5,1 6,1 4,0 5,0
w4 4,2 5,2 6,2 4,1 5,1
w4 4,3 5,3 6,3 4,2 5,2
w4 4,4 5,4 6,4 4,3 5,3
w4 5,1 6,1 7,1 5,0 6,0
w4 5,2 6,2 7,2 5,1 6,1
w4 5,3 6,3 7,3 5,2 6,2
w4 5,4 6,4 7,4 5,3 6,3
w4 6,1 7,1 8,1 6,0 7,0
w4 6,2 7,2 8,2 6,1 7,1
w4 6,3 7,3 8,3 6,2 7,2
w4 6,4 7,4 8,4 6,3 7,3
w4 7,1 8,1 9,1 7,0 8,0
w4 7,2 8,2 9,2 7,1 8,1
w4 7,3 8,3 9,3 7,2 8,2
w4 7,4 8,4 9,4 7,3 8,3
w4 8,1 9,1 10,1 8,0 9,0
w4 8,2 9,2 10,2 8,1 9,1
w4 8,3 9,3 10,3 8,2 9,2
w4 8,4 9,4 10,4 8,3 9,3
w4 1,0 1,1 1,2 0,0 0,1
w4 1,1 1,2 1,3 0,1 0,2
w4 1,2 1,3 1,4 0,2 0,3
w4 2,0 2,1 2,2 1,0 1,1
w4 2,1 2,2 2,3 1,1 1,2
w4 2,2 2,3 2,4 1,2 1,3
w4 3,0 3,1 3,2 2,0 2,1
w4 3,1 3,2 3,3 2,1 2,2
w4 3,2 3,3 3,4 2,2 2,3
w4 4,0 4,1 4,2 3,0 3,1
w4 4,1 4,2 4,3 3,1 3,2
w4 4,2 4,3 4,4 3,2 3,3
w4 5,0 5,1 5,2 4,0 4,1
w4 5,1 5,2 5,3 4,1 4,2
w4 5,2 5,3 5,4 4,2 4,3
w4 6,0 6,1 6,2 5,0 5,1
w4 6,1 6,2 6,3 5,1 5,2
w4 6,2 6,3 6,4 5,2 5,3
w4 7,0 7,1 7,2 6,0 6,1
w4 7,1 7,2 7,3 6,1 6,2
w4 7,2 7,3 7,4 6,2 6,3
w4 8,0 8,1 8,2 7,0 7,1
w4 8,1 8,2 8,3 7,1 7,2
w4 8,2 8,3 8,4 7,2 7,3
w4 9,0 9,1 9,2 8,0 8,1
w4 9,1 9,2 9,3 8,1 8,2
w4 9,2 9,3 9,4 8,2 8,3
w4 10,0 10,1 10,2 9,0 9,1
w4 10,1 10,2 10,3 9,1 9,2
w4 10,2 10,3 10,4 9,2 9,3
w4 0,0 0,1 0,2 1,0 1,1
w4 0,1 0,2 0,3 1,1 1,2
w4 0,2 0,3 0,4 1,2 1,3
w4 1,0 1,1 1,2 2,0 2,1
w4 1,1 1,2 1,3 2,1 2,2
w4 1,2 1,3 1,4 2,2 2,3
w4 2,0 2,1 2,2 3,0 3,1
w4 2,1 2,2 2,3 3,1 3,2
w4 2,2 2,3 2,4 3,2 3,3
w4 3,0 3,1 3,2 4,0 4,1
w4 3,1 3,2 3,3 4,1 4,2
w4 3,2 3,3 3,4 4,2 4,3
w4 4,0 4,1 4,2 5,0 5,1
w4 4,1 4,2 4,3 5,1 5,2
w4 4,2 4,3 4,4 5,2 5,3
w4 5,0 5,1 5,2 6,0 6,1
w4 5,1 5,2 5,3 6,1 6,2
w4 5,2 5,3 5,4 6,2 6,3
w4 6,0 6,1 6,2 7,0 7,1
w4 6,1 6,2 6,3 7,1 7,2
w4 6,2 6,3 6,4 7,2 7,3
w4 7,0 7,1 7,2 8,0 8,1
w4 7,1 7,2 7,3 8,1 8,2
w4 7,2 7,3 7,4 8,2 8,3
w4 8,0 8,1 8,2 9,0 9,1
w4 8,1 8,2 8,3 9,1 9,2
w4 8,2 8,3 8,4 9,2 9,3
w4 9,0 9,1 9,2 10,0 10,1
w4 9,1 9,2 9,3 10,1 10,2
w4 9,2 9,3 9,4 10,2 10,3
w4 2,1 1,1 0,1 2,0 1,0
w4 2,2 1,2 0,2 2,1 1,1
w4 2,3 1,3 0,3 2,2 1,2
w4 2,4 1,4 0,4 2,3 1,3
w4 3,1 2,1 1,1 3,0 2,0
w4 3,2 2,2 1,2 3,1 2,1
w4 3,3 2,3 1,3 3,2 2,2
w4 3,4 2,4 1,4 3,3 2,3
w4 4,1 3,1 2,1 4,0 3,0
w4 4,2 3,2 2,2 4,1 3,1
w4 4,3 3,3 2,3 4,2 3,2
w4 4,4 3,4 2,4 4,3 3,3
w4 5,1 4,1 3,1 5,0 4,0
w4 5,2 4,2 3,2 5,1 4,1
w4 5,3 4,3 3,3 5,2 4,2
w4 5,4 4,4 3,4 5,3 4,3
w4 6,1 5,1 4,1 6,0 5,0
w4 6,2 5,2 4,2 6,1 5,1
w4 6,3 5,3 4,3 6,2 5,2
w4 6,4 5,4 4,4 6,3 5,3
w4 7,1 6,1 5,1 7,0 6,0
w4 7,2 6,2 5,2 7,1 6,1
w4 7,3 6,3 5,3 7,2 6,2
w4 7,4 6,4 5,4 7,3 6,3
w4 8,1 7,1 6,1 8,0 7,0
w4 8,2 7,2 6,2 8,1 7,1
w4 8,3 7,3 6,3 8,2 7,2
w4 8,4 7,4 6,4 8,3 7,3
w4 9,1 8,1 7,1 9,0 8,0
w4 9,2 8,2 7,2 9,1 8,1
w4 9,3 8,3 7,3 9,2 8,2
w4 9,4 8,4 7,4 9,3 8,3
w4 10,1 9,1 8,1 10,0 9,0
w4 10,2 9,2 8,2 10,1 9,1
w4 10,3 9,3 8,3 10,2 9,2
w4 10,4 9,4 8,4 10,3 9,3
w4 2,0 1,0 0,0 2,1 1,1
w4 2,1 1,1 0,1 2,2 1,2
w4 2,2 1,2 0,2 2,3 1,3
w4 2,3 1,3 0,3 2,4 1,4
w4 3,0 2,0 1,0 3,1 2,1
w4 3,1 2,1 1,1 3,2 2,2
w4 3,2 2,2 1,2 3,3 2,3
w4 3,3 2,3 1,3 3,4 2,4
w4 4,0 3,0 2,0 4,1 3,1
w4 4,1 3,1 2,1 4,2 3,2
w4 4,2 3,2 2,2 4,3 3,3
w4 4,3 3,3 2,3 4,4 3,4
w4 5,0 4,0 3,0 5,1 4,1
w4 5,1 4,1 3,1 5,2 4,2
w4 5,2 4,2 3,2 5,3 4,3
w4 5,3 4,3 3,3 5,4 4,4
w4 6,0 5,0 4,0 6,1 5,1
w4 6,1 5,1 4,1 6,2 5,2
w4 6,2 5,2 4,2 6,3 5,3
w4 6,3 5,3 4,3 6,4 5,4
w4 7,0 6,0 5,0 7,1 6,1
w4 7,1 6,1 5,1 7,2 6,2
w4 7,2 6,2 5,2 7,3 6,3
w4 7,3 6,3 5,3 7,4 6,4
w4 8,0 7,0 6,0 8,1 7,1
w4 8,1 7,1 6,1 8,2 7,2
w4 8,2 7,2 6,2 8,3 7,3
w4 8,3 7,3 6,3 8,4 7,4
w4 9,0 8,0 7,0 9,1 8,1
w4 9,1 8,1 7,1 9,2 8,2
w4 9,2 8,2 7,2 9,3 8,3
w4 9,3 8,3 7,3 9,4 8,4
w4 10,0 9,0 8,0 10,1 9,1
w4 10,1 9,1 8,1 10,2 9,2
w4 10,2 9,2 8,2 10,3 9,3
w4 10,3 9,3 8,3 10,4 9,4
w4 0,2 0,1 0,0 1,2 1,1
w4 0,3 0,2 0,1 1,3 1,2
w4 0,4 0,3 0,2 1,4 1,3
w4 1,2 1,1 1,0 2,2 2,1
w4 1,3 1,2 1,1 2,3 2,2
w4 1,4 1,3 1,2 2,4 2,3
w4 2,2 2,1 2,0 3,2 3,1
w4 2,3 2,2 2,1 3,3 3,2
w4 2,4 2,3 2,2 3,4 3,3
w4 3,2 3,1 3,0 4,2 4,1
w4 3,3 3,2 3,1 4,3 4,2
w4 3,4 3,3 3,2 4,4 4,3
w4 4,2 4,1 4,0 5,2 5,1
w4 4,3 4,2 4,1 5,3 5,2
w4 4,4 4,3 4,2 5,4 5,3
w4 5,2 5,1 5,0 6,2 6,1
w4 5,3 5,2 5,1 6,3 6,2
w4 5,4 5,3 5,2 6,4 6,3
w4 6,2 6,1 6,0 7,2 7,1
w4 6,3 6,2 6,1 7,3 7,2
w4 6,4 6,3 6,2 7,4 7,3
w4 7,2 7,1 7,0 8,2 8,1
w4 7,3 7,2 7,1 8,3 8,2
w4 7,4 7,3 7,2 8,4 8,3
w4 8,2 8,1 8,0 9,2 9,1
w4 8,3 8,2 8,1 9,3 9,2
w4 8,4 8,3 8,2 9,4 9,3
w4 9,2 9,1 9,0 10,2 10,1
w4 9,3 9,2 9,1 10,3 10,2
w4 9,4 9,3 9,2 10,4 10,3
w4 1,2 1,1 1,0 0,2 0,1
w4 1,3 1,2 1,1 0,3 0,2
w4 1,4 1,3 1,2 0,4 0,3
w4 2,2 2,1 2,0 1,2 1,1
w4 2,3 2,2 2,1 1,3 1,2
w4 2,4 2,3 2,2 1,4 1,3
w4 3,2 3,1 3,0 2,2 2,1
w4 3,3 3,2 3,1 2,3 2,2
w4 3,4 3,3 3,2 2,4 2,3
w4 4,2 4,1 4,0 3,2 3,1
w4 4,3 4,2 4,1 3,3 3,2
w4 4,4 4,3 4,2 3,4 3,3
w4 5,2 5,1 5,0 4,2 4,1
w4 5,3 5,2 5,1 4,3 4,2
w4 5,4 5,3 5,2 4,4 4,3
w4 6,2 6,1 6,0 5,2 5,1
w4 6,3 6,2 6,1 5,3 5,2
w4 6,4 6,3 6,2 5,4 5,3
w4 7,2 7,1 7,0 6,2 6,1
w4 7,3 7,2 7,1 6,3 6,2
w4 7,4 7,3 7,2 6,4 6,3
w4 8,2 8,1 8,0 7,2 7,1
w4 8,3 8,2 8,1 7,3 7,2
w4 8,4 8,3 8,2 7,4 7,3
w4 9,2 9,1 9,0 8,2 8,1
w4 9,3 9,2 9,1 8,3 8,2
w4 9,4 9,3 9,2 8,4 8,3
w4 10,2 10,1 10,0 9,2 9,1
w4 10,3 10,2 10,1 9,3 9,2
w4 10,4 10,3 10,2 9,4 9,3
w5 1,0 0,1 1,1 2,1 1,2
w5 1,1 0,2 1,2 2,2 1,3
w5 1,2 0,3 1,3 2,3 1,4
w5 2,0 1,1 2,1 3,1 2,2
w5 2,1 1,2 2,2 3,2 2,3
w5 2,2 1,3 2,3 3,3 2,4
w5 3,0 2,1 3,1 4,1 3,2
w5 3,1 2,2 3,2 4,2 3,3
w5 3,2 2,3 3,3 4,3 3,4
w5 4,0 3,1 4,1 5,1 4,2
w5 4,1 3,2 4,2 5,2 4,3
w5 4,2 3,3 4,3 5,3 4,4
w5 5,0 4,1 5,1 6,1 5,2
w5 5,1 4,2 5,2 6,2 5,3
w5 5,2 4,3 5,3 6,3 5,4
w5 6,0 5,1 6,1 7,1 6,2
w5 6,1 5,2 6,2 7,2 6,3
w5 6,2 5,3 6,3 7,3 6,4
w5 7,0 6,1 7,1 8,1 7,2
w5 7,1 6,2 7,2 8,2 7,3
w5 7,2 6,3 7,3 8,3 7,4
w5 8,0 7,1 8,1 9,1 8,2
w5 8,1 7,2 8,2 9,2 8,3
w5 8,2 7,3 8,3 9,3 8,4
w5 9,0 8,1 9,1 10,1 9,2
w5 9,1 8,2 9,2 10,2 9,3
w5 9,2 8,3 9,3 10,3 9,4
w6 0,0 1,0 1,1 2,1 2,2
w6 0,1 1,1 1,2 2,2 2,3
w6 0,2 1,2 1,3 2,3 2,4
w6 1,0 2,0 2,1 3,1 3,2
w6 1,1 2,1 2,2 3,2 3,3
w6 1,2 2,2 2,3 3,3 3,4
w6 2,0 3,0 3,1 4,1 4,2
w6 2,1 3,1 3,2 4,2 4,3
w6 2,2 3,2 3,3 4,3 4,4
w6 3,0 4,0 4,1 5,1 5,2
w6 3,1 4,1 4,2 5,2 5,3
w6 3,2 4,2 4,3 5,3 5,4
w6 4,0 5,0 5,1 6,1 6,2
w6 4,1 5,1 5,2 6,2 6,3
w6 4,2 5,2 5,3 6,3 6,4
w6 5,0 6,0 6,1 7,1 7,2
w6 5,1 6,1 6,2 7,2 7,3
w6 5,2 6,2 6,3 7,3 7,4
w6 6,0 7,0 7,1 8,1 8,2
w6 6,1 7,1 7,2 8,2 8,3
w6 6,2 7,2 7,3 8,3 8,4
w6 7,0 8,0 8,1 9,1 9,2
w6 7,1 8,1 8,2 9,2 9,3
w6 7,2 8,2 8,3 9,3 9,4
w6 8,0 9,0 9,1 10,1 10,2
w6 8,1 9,1 9,2 10,2 10,3
w6 8,2 9,2 9,3 10,3 10,4
w6 2,0 2,1 1,1 1,2 0,2
w6 2,1 2,2 1,2 1,3 0,3
w6 2,2 2,3 1,3 1,4 0,4
w6 3,0 3,1 2,1 2,2 1,2
w6 3,1 3,2 2,2 2,3 1,3
w6 3,2 3,3 2,3 2,4 1,4
w6 4,0 4,1 3,1 3,2 2,2
w6 4,1 4,2 3,2 3,3 2,3
w6 4,2 4,3 3,3 3,4 2,4
w6 5,0 5,1 4,1 4,2 3,2
w6 5,1 5,2 4,2 4,3 3,3
w6 5,2 5,3 4,3 4,4 3,4
w6 6,0 6,1 5,1 5,2 4,2
w6 6,1 6,2 5,2 5,3 4,3
w6 6,2 6,3 5,3 5,4 4,4
w6 7,0 7,1 6,1 6,2 5,2
w6 7,1 7,2 6,2 6,3 5,3
w6 7,2 7,3 6,3 6,4 5,4
w6 8,0 8,1 7,1 7,2 6,2
w6 8,1 8,2 7,2 7,3 6,3
w6 8,2 8,3 7,3 7,4 6,4
w6 9,0 9,1 8,1 8,2 7,2
w6 9,1 9,2 8,2 8,3 7,3
w6 9,2 9,3 8,3 8,4 7,4
w6 10,0 10,1 9,1 9,2 8,2
w6 10,1 10,2 9,2 9,3 8,3
w6 10,2 10,3 9,3 9,4 8,4
w6 2,2 1,2 1,1 0,1 0,0
w6 2,3 1,3 1,2 0,2 0,1
w6 2,4 1,4 1,3 0,3 0,2
w6 3,2 2,2 2,1 1,1 1,0
w6 3,3 2,3 2,2 1,2 1,1
w6 3,4 2,4 2,3 1,3 1,2
w6 4,2 3,2 3,1 2,1 2,0
w6 4,3 3,3 3,2 2,2 2,1
w6 4,4 3,4 3,3 2,3 2,2
w6 5,2 4,2 4,1 3,1 3,0
w6 5,3 4,3 4,2 3,2 3,1
w6 5,4 4,4 4,3 3,3 3,2
w6 6,2 5,2 5,1 4,1 4,0
w6 6,3 5,3 5,2 4,2 4,1
w6 6,4 5,4 5,3 4,3 4,2
w6 7,2 6,2 6,1 5,1 5,0
w6 7,3 6,3 6,2 5,2 5,1
w6 7,4 6,4 6,3 5,3 5,2
w6 8,2 7,2 7,1 6,1 6,0
w6 8,3 7,3 7,2 6,2 6,1
w6 8,4 7,4 7,3 6,3 6,2
w6 9,2 8,2 8,1 7,1 7,0
w6 9,3 8,3 8,2 7,2 7,1
w6 9,4 8,4 8,3 7,3 7,2
w6 10,2 9,2 9,1 8,1 8,0
w6 10,3 9,3 9,2 8,2 8,1
w6 10,4 9,4 9,3 8,3 8,2
w6 0,2 0,1 1,1 1,0 2,0
w6 0,3 0,2 1,2 1,1 2,1
w6 0,4 0,3 1,3 1,2 2,2
w6 1,2 1,1 2,1 2,0 3,0
w6 1,3 1,2 2,2 2,1 3,1
w6 1,4 1,3 2,3 2,2 3,2
w6 2,2 2,1 3,1 3,0 4,0
w6 2,3 2,2 3,2 3,1 4,1
w6 2,4 2,3 3,3 3,2 4,2
w6 3,2 3,1 4,1 4,0 5,0
w6 3,3 3,2 4,2 4,1 5,1
w6 3,4 3,3 4,3 4,2 5,2
w6 4,2 4,1 5,1 5,0 6,0
w6 4,3 4,2 5,2 5,1 6,1
w6 4,4 4,3 5,3 5,2 6,2
w6 5,2 5,1 6,1 6,0 7,0
w6 5,3 5,2 6,2 6,1 7,1
w6 5,4 5,3 6,3 6,2 7,2
w6 6,2 6,1 7,1 7,0 8,0
w6 6,3 6,2 7,2 7,1 8,1
w6 6,4 6,3 7,3 7,2 8,2
w6 7,2 7,1 8,1 8,0 9,0
w6 7,3 7,2 8,2 8,1 9,1
w6 7,4 7,3 8,3 8,2 9,2
w6 8,2 8,1 9,1 9,0 10,0
w6 8,3 8,2 9,2 9,1 10,1
w6 8,4 8,3 9,3 9,2 10,2
w7 0,0 1,0 2,0 2,1 3,1
w7 0,1 1,1 2,1 2,2 3,2
w7 0,2 1,2 2,2 2,3 3,3
w7 0,3 1,3 2,3 2,4 3,4
w7 1,0 2,0 3,0 3,1 4,1
w7 1,1 2,1 3,1 3,2 4,2
w7 1,2 2,2 3,2 3,3 4,3
w7 1,3 2,3 3,3 3,4 4,4
w7 2,0 3,0 4,0 4,1 5,1
w7 2,1 3,1 4,1 4,2 5,2
w7 2,2 3,2 4,2 4,3 5,3
w7 2,3 3,3 4,3 4,4 5,4
w7 3,0 4,0 5,0 5,1 6,1
w7 3,1 4,1 5,1 5,2 6,2
w7 3,2 4,2 5,2 5,3 6,3
w7 3,3 4,3 5,3 5,4 6,4
w7 4,0 5,0 6,0 6,1 7,1
w7 4,1 5,1 6,1 6,2 7,2
w7 4,2 5,2 6,2 6,3 7,3
w7 4,3 5,3 6,3 6,4 7,4
w7 5,0 6,0 7,0 7,1 8,1
w7 5,1 6,1 7,1 7,2 8,2
w7 5,2 6,2 7,2 7,3 8,3
w7 5,3 6,3 7,3 7,4 8,4
w7 6,0 7,0 8,0 8,1 9,1
w7 6,1 7,1 8,1 8,2 9,2
w7 6,2 7,2 8,2 8,3 9,3
w7 6,3 7,3 8,3 8,4 9,4
w7 7,0 8,0 9,0 9,1 10,1
w7 7,1 8,1 9,1 9,2 10,2
w7 7,2 8,2 9,2 9,3 10,3
w7 7,3 8,3 9,3 9,4 10,4
w7 0,1 1,1 2,1 2,0 3,0
w7 0,2 1,2 2,2 2,1 3,1
w7 0,3 1,3 2,3 2,2 3,2
w7 0,4 1,4 2,4 2,3 3,3
w7 1,1 2,1 3,1 3,0 4,0
w7 1,2 2,2 3,2 3,1 4,1
w7 1,3 2,3 3,3 3,2 4,2
w7 1,4 2,4 3,4 3,3 4,3
w7 2,1 3,1 4,1 4,0 5,0
w7 2,2 3,2 4,2 4,1 5,1
w7 2,3 3,3 4,3 4,2 5,2
w7 2,4 3,4 4,4 4,3 5,3
w7 3,1 4,1 5,1 5,0 6,0
w7 3,2 4,2 5,2 5,1 6,1
w7 3,3 4,3 5,3 5,2 6,2
w7 3,4 4,4 5,4 5,3 6,3
w7 4,1 5,1 6,1 6,0 7,0
w7 4,2 5,2 6,2 6,1 7,1
w7 4,3 5,3 6,3 6,2 7,2
w7 4,4 5,4 6,4 6,3 7,3
w7 5,1 6,1 7,1 7,0 8,0
w7 5,2 6,2 7,2 7,1 8,1
w7 5,3 6,3 7,3 7,2 8,2
w7 5,4 6,4 7,4 7,3 8,3
w7 6,1 7,1 8,1 8,0 9,0
w7 6,2 7,2 8,2 8,1 9,1
w7 6,3 7,3 8,3 8,2 9,2
w7 6,4 7,4 8,4 8,3 9,3
w7 7,1 8,1 9,1 9,0 10,0
w7 7,2 8,2 9,2 9,1 10,1
w7 7,3 8,3 9,3 9,2 10,2
w7 7,4 8,4 9,4 9,3 10,3
w7 1,0 1,1 1,2 0,2 0,3
w7 1,1 1,2 1,3 0,3 0,4
w7 2,0 2,1 2,2 1,2 1,3
w7 2,1 2,2 2,3 1,3 1,4
w7 3,0 3,1 3,2 2,2 2,3
w7 3,1 3,2 3,3 2,3 2,4
w7 4,0 4,1 4,2 3,2 3,3
w7 4,1 4,2 4,3 3,3 3,4
w7 5,0 5,1 5,2 4,2 4,3
w7 5,1 5,2 5,3 4,3 4,4
w7 6,0 6,1 6,2 5,2 5,3
w7 6,1 6,2 6,3 5,3 5,4
w7 7,0 7,1 7,2 6,2 6,3
w7 7,1 7,2 7,3 6,3 6,4
w7 8,0 8,1 8,2 7,2 7,3
w7 8,1 8,2 8,3 7,3 7,4
w7 9,0 9,1 9,2 8,2 8,3
w7 9,1 9,2 9,3 8,3 8,4
w7 10,0 10,1 10,2 9,2 9,3
w7 10,1 10,2 10,3 9,3 9,4
w7 0,0 0,1 0,2 1,2 1,3
w7 0,1 0,2 0,3 1,3 1,4
w7 1,0 1,1 1,2 2,2 2,3
w7 1,1 1,2 1,3 2,3 2,4
w7 2,0 2,1 2,2 3,2 3,3
w7 2,1 2,2 2,3 3,3 3,4
w7 3,0 3,1 3,2 4,2 4,3
w7 3,1 3,2 3,3 4,3 4,4
w7 4,0 4,1 4,2 5,2 5,3
w7 4,1 4,2 4,3 5,3 5,4
w7 5,0 5,1 5,2 6,2 6,3
w7 5,1 5,2 5,3 6,3 6,4
w7 6,0 6,1 6,2 7,2 7,3
w7 6,1 6,2 6,3 7,3 7,4
w7 7,0 7,1 7,2 8,2 8,3
w7 7,1 7,2 7,3 8,3 8,4
w7 8,0 8,1 8,2 9,2 9,3
w7 8,1 8,2 8,3 9,3 9,4
w7 9,0 9,1 9,2 10,2 10,3
w7 9,1 9,2 9,3 10,3 10,4
w7 3,1 2,1 1,1 1,0 0,0
w7 3,2 2,2 1,2 1,1 0,1
w7 3,3 2,3 1,3 1,2 0,2
w7 3,4 2,4 1,4 1,3 0,3
w7 4,1 3,1 2,1 2,0 1,0
w7 4,2 3,2 2,2 2,1 1,1
w7 4,3 3,3 2,3 2,2 1,2
w7 4,4 3,4 2,4 2,3 1,3
w7 5,1 4,1 3,1 3,0 2,0
w7 5,2 4,2 3,2 3,1 2,1
w7 5,3 4,3 3,3 3,2 2,2
w7 5,4 4,4 3,4 3,3 2,3
w7 6,1 5,1 4,1 4,0 3,0
w7 6,2 5,2 4,2 4,1 3,1
w7 6,3 5,3 4,3 4,2 3,2
w7 6,4 5,4 4,4 4,3 3,3
w7 7,1 6,1 5,1 5,0 4,0
w7 7,2 6,2 5,2 5,1 4,1
w7 7,3 6,3 5,3 5,2 4,2
w7 7,4 6,4 5,4 5,3 4,3
w7 8,1 7,1 6,1 6,0 5,0
w7 8,2 7,2 6,2 6,1 5,1
w7 8,3 7,3 6,3 6,2 5,2
w7 8,4 7,4 6,4 6,3 5,3
w7 9,1 8,1 7,1 7,0 6,0
w7 9,2 8,2 7,2 7,1 6,1
w7 9,3 8,3 7,3 7,2 6,2
w7 9,4 8,4 7,4 7,3 6,3
w7 10,1 9,1 8,1 8,0 7,0
w7 10,2 9,2 8,2 8,1 7,1
w7 10,3 9,3 8,3 8,2 7,2
w7 10,4 9,4 8,4 8,3 7,3
w7 3,0 2,0 1,0 1,1 0,1
w7 3,1 2,1 1,1 1,2 0,2
w7 3,2 2,2 1,2 1,3 0,3
w7 3,3 2,3 1,3 1,4 0,4
w7 4,0 3,0 2,0 2,1 1,1
w7 4,1 3,1 2,1 2,2 1,2
w7 4,2 3,2 2,2 2,3 1,3
w7 4,3 3,3 2,3 2,4 1,4
w7 5,0 4,0 3,0 3,1 2,1
w7 5,1 4,1 3,1 3,2 2,2
w7 5,2 4,2 3,2 3,3 2,3
w7 5,3 4,3 3,3 3,4 2,4
w7 6,0 5,0 4,0 4,1 3,1
w7 6,1 5,1 4,1 4,2 3,2
w7 6,2 5,2 4,2 4,3 3,3
w7 6,3 5,3 4,3 4,4 3,4
w7 7,0 6,0 5,0 5,1 4,1
w7 7,1 6,1 5,1 5,2 4,2
w7 7,2 6,2 5,2 5,3 4,3
w7 7,3 6,3 5,3 5,4 4,4
w7 8,0 7,0 6,0 6,1 5,1
w7 8,1 7,1 6,1 6,2 5,2
w7 8,2 7,2 6,2 6,3 5,3
w7 8,3 7,3 6,3 6,4 5,4
w7 9,0 8,0 7,0 7,1 6,1
w7 9,1 8,1 7,1 7,2 6,2
w7 9,2 8,2 7,2 7,3 6,3
w7 9,3 8,3 7,3 7,4 6,4
w7 10,0 9,0 8,0 8,1 7,1
w7 10,1 9,1 8,1 8,2 7,2
w7 10,2 9,2 8,2 8,3 7,3
w7 10,3 9,3 8,3 8,4 7,4
w7 0,3 0,2 0,1 1,1 1,0
w7 0,4 0,3 0,2 1,2 1,1
w7 1,3 1,2 1,1 2,1 2,0
w7 1,4 1,3 1,2 2,2 2,1
w7 2,3 2,2 2,1 3,1 3,0
w7 2,4 2,3 2,2 3,2 3,1
w7 3,3 3,2 3,1 4,1 4,0
w7 3,4 3,3 3,2 4,2 4,1
w7 4,3 4,2 4,1 5,1 5,0
w7 4,4 4,3 4,2 5,2 5,1
w7 5,3 5,2 5,1 6,1 6,0
w7 5,4 5,3 5,2 6,2 6,1
w7 6,3 6,2 6,1 7,1 7,0
w7 6,4 6,3 6,2 7,2 7,1
w7 7,3 7,2 7,1 8,1 8,0
w7 7,4 7,3 7,2 8,2 8,1
w7 8,3 8,2 8,1 9,1 9,0
w7 8,4 8,3 8,2 9,2 9,1
w7 9,3 9,2 9,1 10,1 10,0
w7 9,4 9,3 9,2 10,2 10,1
w7 1,3 1,2 1,1 0,1 0,0
w7 1,4 1,3 1,2 0,2 0,1
w7 2,3 2,2 2,1 1,1 1,0
w7 2,4 2,3 2,2 1,2 1,1
w7 3,3 3,2 3,1 2,1 2,0
w7 3,4 3,3 3,2 2,2 2,1
w7 4,3 4,2 4,1 3,1 3,0
w7 4,4 4,3 4,2 3,2 3,1
w7 5,3 5,2 5,1 4,1 4,0
w7 5,4 5,3 5,2 4,2 4,1
w7 6,3 6,2 6,1 5,1 5,0
w7 6,4 6,3 6,2 5,2 5,1
w7 7,3 7,2 7,1 6,1 6,0
w7 7,4 7,3 7,2 6,2 6,1
w7 8,3 8,2 8,1 7,1 7,0
w7 8,4 8,3 8,2 7,2 7,1
w7 9,3 9,2 9,1 8,1 8,0
w7 9,4 9,3 9,2 8,2 8,1
w7 10,3 10,2 10,1 9,1 9,0
w7 10,4 10,3 10,2 9,2 9,1
w8 0,0 1,0 1,1
w8 0,1 1,1 1,2
w8 0,2 1,2 1,3
w8 0,3 1,3 1,4
w8 1,0 2,0 2,1
w8 1,1 2,1 2,2
w8 1,2 2,2 2,3
w8 1,3 2,3 2,4
w8 2,0 3,0 3,1
w8 2,1 3,1 3,2
w8 2,2 3,2 3,3
w8 2,3 3,3 3,4
w8 3,0 4,0 4,1
w8 3,1 4,1 4,2
w8 3,2 4,2 4,3
w8 3,3 4,3 4,4
w8 4,0 5,0 5,1
w8 4,1 5,1 5,2
w8 4,2 5,2 5,3
w8 4,3 5,3 5,4
w8 5,0 6,0 6,1
w8 5,1 6,1 6,2
w8 5,2 6,2 6,3
w8 5,3 6,3 6,4
w8 6,0 7,0 7,1
w8 6,1 7,1 7,2
w8 6,2 7,2 7,3
w8 6,3 7,3 7,4
w8 7,0 8,0 8,1
w8 7,1 8,1 8,2
w8 7,2 8,2 8,3
w8 7,3 8,3 8,4
w8 8,0 9,0 9,1
w8 8,1 9,1 9,2
w8 8,2 9,2 9,3
w8 8,3 9,3 9,4
w8 9,0 10,0 10,1
w8 9,1 10,1 10,2
w8 9,2 10,2 10,3
w8 9,3 10,3 10,4
w8 1,0 1,1 0,1
w8 1,1 1,2 0,2
w8 1,2 1,3 0,3
w8 1,3 1,4 0,4
w8 2,0 2,1 1,1
w8 2,1 2,2 1,2
w8 2,2 2,3 1,3
w8 2,3 2,4 1,4
w8 3,0 3,1 2,1
w8 3,1 3,2 2,2
w8 3,2 3,3 2,3
w8 3,3 3,4 2,4
w8 4,0 4,1 3,1
w8 4,1 4,2 3,2
w8 4,2 4,3 3,3
w8 4,3 4,4 3,4
w8 5,0 5,1 4,1
w8 5,1 5,2 4,2
w8 5,2 5,3 4,3
w8 5,3 5,4 4,4
w8 6,0 6,1 5,1
w8 6,1 6,2 5,2
w8 6,2 6,3 5,3
w8 6,3 6,4 5,4
w8 7,0 7,1 6,1
w8 7,1 7,2 6,2
w8 7,2 7,3 6,3
w8 7,3 7,4 6,4
w8 8,0 8,1 7,1
w8 8,1 8,2 7,2
w8 8,2 8,3 7,3
w8 8,3 8,4 7,4
w8 9,0 9,1 8,1
w8 9,1 9,2 8,2
w8 9,2 9,3 8,3
w8 9,3 9,4 8,4
w8 10,0 10,1 9,1
w8 10,1 10,2 9,2
w8 10,2 10,3 9,3
w8 10,3 10,4 9,4
w8 1,1 0,1 0,0
w8 1,2 0,2 0,1
w8 1,3 0,3 0,2
w8 1,4 0,4 0,3
w8 2,1 1,1 1,0
w8 2,2 1,2 1,1
w8 2,3 1,3 1,2
w8 2,4 1,4 1,3
w8 3,1 2,1 2,0
w8 3,2 2,2 2,1
w8 3,3 2,3 2,2
w8 3,4 2,4 2,3
w8 4,1 3,1 3,0
w8 4,2 3,2 3,1
w8 4,3 3,3 3,2
w8 4,4 3,4 3,3
w8 5,1 4,1 4,0
w8 5,2 4,2 4,1
w8 5,3 4,3 4,2
w8 5,4 4,4 4,3
w8 6,1 5,1 5,0
w8 6,2 5,2 5,1
w8 6,3 5,3 5,2
w8 6,4 5,4 5,3
w8 7,1 6,1 6,0
w8 7,2 6,2 6,1
w8 7,3 6,3 6,2
w8 7,4 6,4 6,3
w8 8,1 7,1 7,0
w8 8,2 7,2 7,1
w8 8,3 7,3 7,2
w8 8,4 7,4 7,3
w8 9,1 8,1 8,0
w8 9,2 8,2 8,1
w8 9,3 8,3 8,2
w8 9,4 8,4 8,3
w8 10,1 9,1 9,0
w8 10,2 9,2 9,1
w8 10,3 9,3 9,2
w8 10,4 9,4 9,3
w8 0,1 0,0 1,0
w8 0,2 0,1 1,1
w8 0,3 0,2 1,2
w8 0,4 0,3 1,3
w8 1,1 1,0 2,0
w8 1,2 1,1 2,1
w8 1,3 1,2 2,2
w8 1,4 1,3 2,3
w8 2,1 2,0 3,0
w8 2,2 2,1 3,1
w8 2,3 2,2 3,2
w8 2,4 2,3 3,3
w8 3,1 3,0 4,0
w8 3,2 3,1 4,1
w8 3,3 3,2 4,2
w8 3,4 3,3 4,3
w8 4,1 4,0 5,0
w8 4,2 4,1 5,1
w8 4,3 4,2 5,2
w8 4,4 4,3 5,3
w8 5,1 5,0 6,0
w8 5,2 5,1 6,1
w8 5,3 5,2 6,2
w8 5,4 5,3 6,3
w8 6,1 6,0 7,0
w8 6,2 6,1 7,1
w8 6,3 6,2 7,2
w8 6,4 6,3 7,3
w8 7,1 7,0 8,0
w8 7,2 7,1 8,1
w8 7,3 7,2 8,2
w8 7,4 7,3 8,3
w8 8,1 8,0 9,0
w8 8,2 8,1 9,1
w8 8,3 8,2 9,2
w8 8,4 8,3 9,3
w8 9,1 9,0 10,0
w8 9,2 9,1 10,1
w8 9,3 9,2 10,2
w8 9,4 9,3 10,3
w9 0,0 1,0 0,1 1,1
w9 0,1 1,1 0,2 1,2
w9 0,2 1,2 0,3 1,3
w9 0,3 1,3 0,4 1,4
w9 1,0 2,0 1,1 2,1
w9 1,1 2,1 1,2 2,2
w9 1,2 2,2 1,3 2,3
w9 1,3 2,3 1,4 2,4
w9 2,0 3,0 2,1 3,1
w9 2,1 3,1 2,2 3,2
w9 2,2 3,2 2,3 3,3
w9 2,3 3,3 2,4 3,4
w9 3,0 4,0 3,1 4,1
w9 3,1 4,1 3,2 4,2
w9 3,2 4,2 3,3 4,3
w9 3,3 4,3 3,4 4,4
w9 4,0 5,0 4,1 5,1
w9 4,1 5,1 4,2 5,2
w9 4,2 5,2 4,3 5,3
w9 4,3 5,3 4,4 5,4
w9 5,0 6,0 5,1 6,1
w9 5,1 6,1 5,2 6,2
w9 5,2 6,2 5,3 6,3
w9 5,3 6,3 5,4 6,4
w9 6,0 7,0 6,1 7,1
w9 6,1 7,1 6,2 7,2
w9 6,2 7,2 6,3 7,3
w9 6,3 7,3 6,4 7,4
w9 7,0 8,0 7,1 8,1
w9 7,1 8,1 7,2 8,2
w9 7,2 8,2 7,3 8,3
w9 7,3 8,3 7,4 8,4
w9 8,0 9,0 8,1 9,1
w9 8,1 9,1 8,2 9,2
w9 8,2 9,2 8,3 9,3
w9 8,3 9,3 8,4 9,4
w9 9,0 10,0 9,1 10,1
w9 9,1 10,1 9,2 10,2
w9 9,2 10,2 9,3 10,3
w9 9,3 10,3 9,4 10,4
w10 0,0 1,0 2,0 0,1 2,1
w10 0,1 1,1 2,1 0,2 2,2
w10 0,2 1,2 2,2 0,3 2,3
w10 0,3 1,3 2,3 0,4 2,4
w10 1,0 2,0 3,0 1,1 3,1
w10 1,1 2,1 3,1 1,2 3,2
w10 1,2 2,2 3,2 1,3 3,3
w10 1,3 2,3 3,3 1,4 3,4
w10 2,0 3,0 4,0 2,1 4,1
w10 2,1 3,1 4,1 2,2 4,2
w10 2,2 3,2 4,2 2,3 4,3
w10 2,3 3,3 4,3 2,4 4,4
w10 3,0 4,0 5,0 3,1 5,1
w10 3,1 4,1 5,1 3,2 5,2
w10 3,2 4,2 5,2 3,3 5,3
w10 3,3 4,3 5,3 3,4 5,4
w10 4,0 5,0 6,0 4,1 6,1
w10 4,1 5,1 6,1 4,2 6,2
w10 4,2 5,2 6,2 4,3 6,3
w10 4,3 5,3 6,3 4,4 6,4
w10 5,0 6,0 7,0 5,1 7,1
w10 5,1 6,1 7,1 5,2 7,2
w10 5,2 6,2 7,2 5,3 7,3
w10 5,3 6,3 7,3 5,4 7,4
w10 6,0 7,0 8,0 6,1 8,1
w10 6,1 7,1 8,1 6,2 8,2
w10 6,2 7,2 8,2 6,3 8,3
w10 6,3 7,3 8,3 6,4 8,4
w10 7,0 8,0 9,0 7,1 9,1
w10 7,1 8,1 9,1 7,2 9,2
w10 7,2 8,2 9,2 7,3 9,3
w10 7,3 8,3 9,3 7,4 9,4
w10 8,0 9,0 10,0 8,1 10,1
w10 8,1 9,1 10,1 8,2 10,2
w10 8,2 9,2 10,2 8,3 10,3
w10 8,3 9,3 10,3 8,4 10,4
w10 1,0 1,1 1,2 0,0 0,2
w10 1,1 1,2 1,3 0,1 0,3
w10 1,2 1,3 1,4 0,2 0,4
w10 2,0 2,1 2,2 1,0 1,2
w10 2,1 2,2 2,3 1,1 1,3
w10 2,2 2,3 2,4 1,2 1,4
w10 3,0 3,1 3,2 2,0 2,2
w10 3,1 3,2 3,3 2,1 2,3
w10 3,2 3,3 3,4 2,2 2,4
w10 4,0 4,1 4,2 3,0 3,2
w10 4,1 4,2 4,3 3,1 3,3
w10 4,2 4,3 4,4 3,2 3,4
w10 5,0 5,1 5,2 4,0 4,2
w10 5,1 5,2 5,3 4,1 4,3
w10 5,2 5,3 5,4 4,2 4,4
w10 6,0 6,1 6,2 5,0 5,2
w10 6,1 6,2 6,3 5,1 5,3
w10 6,2 6,3 6,4 5,2 5,4
w10 7,0 7,1 7,2 6,0 6,2
w10 7,1 7,2 7,3 6,1 6,3
w10 7,2 7,3 7,4 6,2 6,4
w10 8,0 8,1 8,2 7,0 7,2
w10 8,1 8,2 8,3 7,1 7,3
w10 8,2 8,3 8,4 7,2 7,4
w10 9,0 9,1 9,2 8,0 8,2
w10 9,1 9,2 9,3 8,1 8,3
w10 9,2 9,3 9,4 8,2 8,4
w10 10,0 10,1 10,2 9,0 9,2
w10 10,1 10,2 10,3 9,1 9,3
w10 10,2 10,3 10,4 9,2 9,4
w10 2,1 1,1 0,1 2,0 0,0
w10 2,2 1,2 0,2 2,1 0,1
w10 2,3 1,3 0,3 2,2 0,2
w10 2,4 1,4 0,4 2,3 0,3
w10 3,1 2,1 1,1 3,0 1,0
w10 3,2 2,2 1,2 3,1 1,1
w10 3,3 2,3 1,3 3,2 1,2
w10 3,4 2,4 1,4 3,3 1,3
w10 4,1 3,1 2,1 4,0 2,0
w10 4,2 3,2 2,2 4,1 2,1
w10 4,3 3,3 2,3 4,2 2,2
w10 4,4 3,4 2,4 4,3 2,3
w10 5,1 4,1 3,1 5,0 3,0
w10 5,2 4,2 3,2 5,1 3,1
w10 5,3 4,3 3,3 5,2 3,2
w10 5,4 4,4 3,4 5,3 3,3
w10 6,1 5,1 4,1 6,0 4,0
w10 6,2 5,2 4,2 6,1 4,1
w10 6,3 5,3 4,3 6,2 4,2
w10 6,4 5,4 4,4 6,3 4,3
w10 7,1 6,1 5,1 7,0 5,0
w10 7,2 6,2 5,2 7,1 5,1
w10 7,3 6,3 5,3 7,2 5,2
w10 7,4 6,4 5,4 7,3 5,3
w10 8,1 7,1 6,1 8,0 6,0
w10 8,2 7,2 6,2 8,1 6,1
w10 8,3 7,3 6,3 8,2 6,2
w10 8,4 7,4 6,4 8,3 6,3
w10 9,1 8,1 7,1 9,0 7,0
w10 9,2 8,2 7,2 9,1 7,1
w10 9,3 8,3 7,3 9,2 7,2
w10 9,4 8,4 7,4 9,3 7,3
w10 10,1 9,1 8,1 10,0 8,0
w10 10,2 9,2 8,2 10,1 8,1
w10 10,3 9,3 8,3 10,2 8,2
w10 10,4 9,4 8,4 10,3 8,3
w10 0,2 0,1 0,0 1,2 1,0
w10 0,3 0,2 0,1 1,3 1,1
w10 0,4 0,3 0,2 1,4 1,2
w10 1,2 1,1 1,0 2,2 2,0
w10 1,3 1,2 1,1 2,3 2,1
w10 1,4 1,3 1,2 2,4 2,2
w10 2,2 2,1 2,0 3,2 3,0
w10 2,3 2,2 2,1 3,3 3,1
w10 2,4 2,3 2,2 3,4 3,2
w10 3,2 3,1 3,0 4,2 4,0
w10 3,3 3,2 3,1 4,3 4,1
w10 3,4 3,3 3,2 4,4 4,2
w10 4,2 4,1 4,0 5,2 5,0
w10 4,3 4,2 4,1 5,3 5,1
w10 4,4 4,3 4,2 5,4 5,2
w10 5,2 5,1 5,0 6,2 6,0
w10 5,3 5,2 5,1 6,3 6,1
w10 5,4 5,3 5,2 6,4 6,2
w10 6,2 6,1 6,0 7,2 7,0
w10 6,3 6,2 6,1 7,3 7,1
w10 6,4 6,3 6,2 7,4 7,2
w10 7,2 7,1 7,0 8,2 8,0
w10 7,3 7,2 7,1 8,3 8,1
w10 7,4 7,3 7,2 8,4 8,2
w10 8,2 8,1 8,0 9,2 9,0
w10 8,3 8,2 8,1 9,3 9,1
w10 8,4 8,3 8,2 9,4 9,2
w10 9,2 9,1 9,0 10,2 10,0
w10 9,3 9,2 9,1 10,3 10,1
w10 9,4 9,3 9,2 10,4 10,2
w11 0,0 1,0 2,0 3,0 2,1
w11 0,1 1,1 2,1 3,1 2,2
w11 0,2 1,2 2,2 3,2 2,3
w11 0,3 1,3 2,3 3,3 2,4
w11 1,0 2,0 3,0 4,0 3,1
w11 1,1 2,1 3,1 4,1 3,2
w11 1,2 2,2 3,2 4,2 3,3
w11 1,3 2,3 3,3 4,3 3,4
w11 2,0 3,0 4,0 5,0 4,1
w11 2,1 3,1 4,1 5,1 4,2
w11 2,2 3,2 4,2 5,2 4,3
w11 2,3 3,3 4,3 5,3 4,4
w11 3,0 4,0 5,0 6,0 5,1
w11 3,1 4,1 5,1 6,1 5,2
w11 3,2 4,2 5,2 6,2 5,3
w11 3,3 4,3 5,3 6,3 5,4
w11 4,0 5,0 6,0 7,0 6,1
w11 4,1 5,1 6,1 7,1 6,2
w11 4,2 5,2 6,2 7,2 6,3
w11 4,3 5,3 6,3 7,3 6,4
w11 5,0 6,0 7,0 8,0 7,1
w11 5,1 6,1 7,1 8,1 7,2
w11 5,2 6,2 7,2 8,2 7,3
w11 5,3 6,3 7,3 8,3 7,4
w11 6,0 7,0 8,0 9,0 8,1
w11 6,1 7,1 8,1 9,1 8,2
w11 6,2 7,2 8,2 9,2 8,3
w11 6,3 7,3 8,3 9,3 8,4
w11 7,0 8,0 9,0 10,0 9,1
w11 7,1 8,1 9,1 10,1 9,2
w11 7,2 8,2 9,2 10,2 9,3
w11 7,3 8,3 9,3 10,3 9,4
w11 0,1 1,1 2,1 3,1 2,0
w11 0,2 1,2 2,2 3,2 2,1
w11 0,3 1,3 2,3 3,3 2,2
w11 0,4 1,4 2,4 3,4 2,3
w11 1,1 2,1 3,1 4,1 3,0
w11 1,2 2,2 3,2 4,2 3,1
w11 1,3 2,3 3,3 4,3 3,2
w11 1,4 2,4 3,4 4,4 3,3
w11 2,1 3,1 4,1 5,1 4,0
w11 2,2 3,2 4,2 5,2 4,1
w11 2,3 3,3 4,3 5,3 4,2
w11 2,4 3,4 4,4 5,4 4,3
w11 3,1 4,1 5,1 6,1 5,0
w11 3,2 4,2 5,2 6,2 5,1
w11 3,3 4,3 5,3 6,3 5,2
w11 3,4 4,4 5,4 6,4 5,3
w11 4,1 5,1 6,1 7,1 6,0
w11 4,2 5,2 6,2 7,2 6,1
w11 4,3 5,3 6,3 7,3 6,2
w11 4,4 5,4 6,4 7,4 6,3
w11 5,1 6,1 7,1 8,1 7,0
w11 5,2 6,2 7,2 8,2 7,1
w11 5,3 6,3 7,3 8,3 7,2
w11 5,4 6,4 7,4 8,4 7,3
w11 6,1 7,1 8,1 9,1 8,0
w11 6,2 7,2 8,2 9,2 8,1
w11 6,3 7,3 8,3 9,3 8,2
w11 6,4 7,4 8,4 9,4 8,3
w11 7,1 8,1 9,1 10,1 9,0
w11 7,2 8,2 9,2 10,2 9,1
w11 7,3 8,3 9,3 10,3 9,2
w11 7,4 8,4 9,4 10,4 9,3
w11 1,0 1,1 1,2 1,3 0,2
w11 1,1 1,2 1,3 1,4 0,3
w11 2,0 2,1 2,2 2,3 1,2
w11 2,1 2,2 2,3 2,4 1,3
w11 3,0 3,1 3,2 3,3 2,2
w11 3,1 3,2 3,3 3,4 2,3
w11 4,0 4,1 4,2 4,3 3,2
w11 4,1 4,2 4,3 4,4 3,3
w11 5,0 5,1 5,2 5,3 4,2
w11 5,1 5,2 5,3 5,4 4,3
w11 6,0 6,1 6,2 6,3 5,2
w11 6,1 6,2 6,3 6,4 5,3
w11 7,0 7,1 7,2 7,3 6,2
w11 7,1 7,2 7,3 7,4 6,3
w11 8,0 8,1 8,2 8,3 7,2
w11 8,1 8,2 8,3 8,4 7,3
w11 9,0 9,1 9,2 9,3 8,2
w11 9,1 9,2 9,3 9,4 8,3
w11 10,0 10,1 10,2 10,3 9,2
w11 10,1 10,2 10,3 10,4 9,3
w11 0,0 0,1 0,2 0,3 1,2
w11 0,1 0,2 0,3 0,4 1,3
w11 1,0 1,1 1,2 1,3 2,2
w11 1,1 1,2 1,3 1,4 2,3
w11 2,0 2,1 2,2 2,3 3,2
w11 2,1 2,2 2,3 2,4 3,3
w11 3,0 3,1 3,2 3,3 4,2
w11 3,1 3,2 3,3 3,4 4,3
w11 4,0 4,1 4,2 4,3 5,2
w11 4,1 4,2 4,3 4,4 5,3
w11 5,0 5,1 5,2 5,3 6,2
w11 5,1 5,2 5,3 5,4 6,3
w11 6,0 6,1 6,2 6,3 7,2
w11 6,1 6,2 6,3 6,4 7,3
w11 7,0 7,1 7,2 7,3 8,2
w11 7,1 7,2 7,3 7,4 8,3
w11 8,0 8,1 8,2 8,3 9,2
w11 8,1 8,2 8,3 8,4 9,3
w11 9,0 9,1 9,2 9,3 10,2
w11 9,1 9,2 9,3 9,4 10,3
w11 3,1 2,1 1,1 0,1 1,0
w11 3,2 2,2 1,2 0,2 1,1
w11 3,3 2,3 1,3 0,3 1,2
w11 3,4 2,4 1,4 0,4 1,3
w11 4,1 3,1 2,1 1,1 2,0
w11 4,2 3,2 2,2 1,2 2,1
w11 4,3 3,3 2,3 1,3 2,2
w11 4,4 3,4 2,4 1,4 2,3
w11 5,1 4,1 3,1 2,1 3,0
w11 5,2 4,2 3,2 2,2 3,1
w11 5,3 4,3 3,3 2,3 3,2
w11 5,4 4,4 3,4 2,4 3,3
w11 6,1 5,1 4,1 3,1 4,0
w11 6,2 5,2 4,2 3,2 4,1
w11 6,3 5,3 4,3 3,3 4,2
w11 6,4 5,4 4,4 3,4 4,3
w11 7,1 6,1 5,1 4,1 5,0
w11 7,2 6,2 5,2 4,2 5,1
w11 7,3 6,3 5,3 4,3 5,2
w11 7,4 6,4 5,4 4,4 5,3
w11 8,1 7,1 6,1 5,1 6,0
w11 8,2 7,2 6,2 5,2 6,1
w11 8,3 7,3 6,3 5,3 6,2
w11 8,4 7,4 6,4 5,4 6,3
w11 9,1 8,1 7,1 6,1 7,0
w11 9,2 8,2 7,2 6,2 7,1
w11 9,3 8,3 7,3 6,3 7,2
w11 9,4 8,4 7,4 6,4 7,3
w11 10,1 9,1 8,1 7,1 8,0
w11 10,2 9,2 8,2 7,2 8,1
w11 10,3 9,3 8,3 7,3 8,2
w11 10,4 9,4 8,4 7,4 8,3
w11 3,0 2,0 1,0 0,0 1,1
w11 3,1 2,1 1,1 0,1 1,2
w11 3,2 2,2 1,2 0,2 1,3
w11 3,3 2,3 1,3 0,3 1,4
w11 4,0 3,0 2,0 1,0 2,1
w11 4,1 3,1 2,1 1,1 2,2
w11 4,2 3,2 2,2 1,2 2,3
w11 4,3 3,3 2,3 1,3 2,4
w11 5,0 4,0 3,0 2,0 3,1
w11 5,1 4,1 3,1 2,1 3,2
w11 5,2 4,2 3,2 2,2 3,3
w11 5,3 4,3 3,3 2,3 3,4
w11 6,0 5,0 4,0 3,0 4,1
w11 6,1 5,1 4,1 3,1 4,2
w11 6,2 5,2 4,2 3,2 4,3
w11 6,3 5,3 4,3 3,3 4,4
w11 7,0 6,0 5,0 4,0 5,1
w11 7,1 6,1 5,1 4,1 5,2
w11 7,2 6,2 5,2 4,2 5,3
w11 7,3 6,3 5,3 4,3 5,4
w11 8,0 7,0 6,0 5,0 6,1
w11 8,1 7,1 6,1 5,1 6,2
w11 8,2 7,2 6,2 5,2 6,3
w11 8,3 7,3 6,3 5,3 6,4
w11 9,0 8,0 7,0 6,0 7,1
w11 9,1 8,1 7,1 6,1 7,2
w11 9,2 8,2 7,2 6,2 7,3
w11 9,3 8,3 7,3 6,3 7,4
w11 10,0 9,0 8,0 7,0 8,1
w11 10,1 9,1 8,1 7,1 8,2
w11 10,2 9,2 8,2 7,2 8,3
w11 10,3 9,3 8,3 7,3 8,4
w11 0,3 0,2 0,1 0,0 1,1
w11 0,4 0,3 0,2 0,1 1,2
w11 1,3 1,2 1,1 1,0 2,1
w11 1,4 1,3 1,2 1,1 2,2
w11 2,3 2,2 2,1 2,0 3,1
w11 2,4 2,3 2,2 2,1 3,2
w11 3,3 3,2 3,1 3,0 4,1
w11 3,4 3,3 3,2 3,1 4,2
w11 4,3 4,2 4,1 4,0 5,1
w11 4,4 4,3 4,2 4,1 5,2
w11 5,3 5,2 5,1 5,0 6,1
w11 5,4 5,3 5,2 5,1 6,2
w11 6,3 6,2 6,1 6,0 7,1
w11 6,4 6,3 6,2 6,1 7,2
w11 7,3 7,2 7,1 7,0 8,1
w11 7,4 7,3 7,2 7,1 8,2
w11 8,3 8,2 8,1 8,0 9,1
w11 8,4 8,3 8,2 8,1 9,2
w11 9,3 9,2 9,1 9,0 10,1
w11 9,4 9,3 9,2 9,1 10,2
w11 1,3 1,2 1,1 1,0 0,1
w11 1,4 1,3 1,2 1,1 0,2
w11 2,3 2,2 2,1 2,0 1,1
w11 2,4 2,3 2,2 2,1 1,2
w11 3,3 3,2 3,1 3,0 2,1
w11 3,4 3,3 3,2 3,1 2,2
w11 4,3 4,2 4,1 4,0 3,1
w11 4,4 4,3 4,2 4,1 3,2
w11 5,3 5,2 5,1 5,0 4,1
w11 5,4 5,3 5,2 5,1 4,2
w11 6,3 6,2 6,1 6,0 5,1
w11 6,4 6,3 6,2 6,1 5,2
w11 7,3 7,2 7,1 7,0 6,1
w11 7,4 7,3 7,2 7,1 6,2
w11 8,3 8,2 8,1 8,0 7,1
w11 8,4 8,3 8,2 8,1 7,2
w11 9,3 9,2 9,1 9,0 8,1
w11 9,4 9,3 9,2 9,1 8,2
w11 10,3 10,2 10,1 10,0 9,1
w11 10,4 10,3 10,2 10,1 9,2"""


pfill = .8


class board:
    def __init__(self, posi, len, lon, w, h):
        self.w = w
        self.h = h
        self.dim = [len, lon]
        self.holes = []  # all the holes (just for visualization)
        self.circles = []
        for i in range(w):
            for j in range(h):
                self._add_hole(posi + vector(i * len / w, j * lon / h, 0))
                self._add_sphere(posi + vector(i * len / w, j * lon / h, .25))

                #    def get(self, i, j):
                #        if i < 0 or i >= self.w:
                #            return False
                #        if j < 0 or j >= self.h:
                #            return False
                #        return self.bools[i + j * self.w]
                #
                #    def add_piece(self, p, pose=None):
                #        if pose is not None:
                #            p.setpos(pose)
                #        spots = p.get_spots()
                #        for spot in spots:
                #            if self.get(spot.x, spot.y):
                #                return False
                #        for spot in spots:
                #            self.bools[spot.x + spot.y * self.w] = True
                #        self.pieces.append(p)
                #        p.set_visible()
                #
                #    def remove_last(self):
                #        for spot in self.pieces[-1].get_spots():
                #            self.bools[spot.x + spot.y * self.w] = False
                #        self.pieces[-1].set_invisible()
                #        self.pieces = self.pieces[:-1]

    def _add_hole(self, posi):
        pass

    def _add_sphere(self, posi):
        pass

    def set(self, i, j, col):
        pass

    def clear(self):
        pass


class node:
    def __init__(self, up, down, aux):
        self.up = up
        self.down = down
        self.aux = aux


class item:
    def __init__(self, name, left, right):
        self.name = name
        self.left = left
        self.right = right

    def __eq__(self, other):
        return other == self.name


def hide(nodes, p):
    q = p + 1
    while q != p:
        x = nodes[q].aux
        u = nodes[q].up
        d = nodes[q].down
        if x <= 0:
            q = u
        else:
            nodes[u].down = d
            nodes[d].up = u
            nodes[x].aux -= 1
            q += 1


def cover(nodes, items, i):
    p = nodes[i].down
    while p != i:
        hide(nodes, p)
        p = nodes[p].down
    l = items[i].left
    r = items[i].right
    items[l].right = r
    items[r].left = l


def unhide(nodes, p):
    q = p - 1
    while q != p:
        x = nodes[q].aux
        u = nodes[q].up
        d = nodes[q].down
        if x <= 0:
            q = d
        else:
            nodes[u].down = q
            nodes[d].up = q
            nodes[x].aux += 1
            q -= 1


def uncover(nodes, items, i):
    l = items[i].left
    r = items[i].right
    items[l].right = i
    items[r].left = i
    p = nodes[i].up
    while p != i:
        unhide(nodes, p)
        p = nodes[p].up


def get_index(nodes, xl):
    # gets the index of the option containing node xl
    while nodes[xl].aux > 0:
        xl -= 1
    return -nodes[xl].aux


# colormap = {'w0': color.purple, 'w1': color.blue, 'w2': color.orange, 'w3': vector(.5, .85, 1), 'w4': color.red,
#             'w5': vector(.6, .6, .6),
#             'w6': vector(1, .41, .71), 'w7': vector(0, .7, .1), 'w8': vector(.9, .85, .85), 'w9': color.green,
#             'w10': color.yellow, 'w11': vector(1, .7, .7)}

b = board(vector(0, 0, -.25), 11, 5, 11, 5)


def create_board_setup(nodes, items, soln):
    print('cu')
    b.clear()
    for option in soln:
        col = None# colormap[option[0]]
        for tile in option[1:]:
            i, j = tile.split(',')
            x = int(i)
            y = int(j)
            b.set(x, y, col)


def selp(nodes, items, options, partial_soln):
    if items[0].right == 0:
        yield [options[xl] for xl in partial_soln]
    else:
        min_seen = -1
        min_index = 0
        find = items[0].right
        while find != 0:
            m = nodes[find].aux
            if m < min_seen or min_seen == -1:
                min_seen = m
                min_index = find
            find = items[find].right

        i = min_index
        cover(nodes, items, i)
        xl = nodes[i].down
        while xl != i:
            p = xl + 1
            while p != xl:
                j = nodes[p].aux
                if j <= 0:
                    p = nodes[p].up
                else:
                    cover(nodes, items, j)
                    p += 1
            for s in selp(nodes, items, options, partial_soln + [get_index(nodes, xl)]):
                yield s

            p = xl - 1
            while p != xl:
                j = nodes[p].aux
                if j <= 0:
                    p = nodes[p].down
                else:
                    uncover(nodes, items, j)
                    p -= 1
            xl = nodes[xl].down
        uncover(nodes, items, i)


def parse_file():
    file = st.splitlines()
    itms = ['_'] + file[0].strip().split(' ')
    items = [item(i, loc - 1, loc + 1) for i, loc in zip(itms, range(len(itms)))]
    items[0].left = len(items) - 1
    items[-1].right = 0
    nodes = [node(x, x, 0) for x in range(len(itms))]
    p = len(nodes)

    first_in_row = 0
    nodes.append(node(first_in_row, 0, 0))
    last_spacer = nodes[-1]
    num_spacers = 1
    options = []

    for line in file[1:]:
        first_in_row = 0
        p += 1
        options.append(line.strip().split(' '))
        for opt in options[-1]:
            i = itms.index(opt)
            itm = nodes[i]
            itm.aux += 1
            nodes.append(node(itm.up, i, i))
            nodes[itm.up].down = p
            nodes[i].up = p
            if first_in_row == 0:
                first_in_row = p
            p += 1
        last_spacer.down = p - 1

        nodes.append(node(first_in_row, 0, -num_spacers))
        last_spacer = nodes[-1]
        num_spacers += 1
    return nodes, items, options


def solve():
    nodes, items, options = parse_file()
    for s in selp(nodes, items, options, []):
        create_board_setup(nodes, items, s)
        yield s


lenf = 1

for s in solve():
    pass






