import pygame


pygame.init()
screen = pygame.display.set_mode((640, 480))
screen.convert()
pygame.display.set_caption('Kanoodle')


pfill = .8


class vector:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, v):
        return vector(self.x + v.x, self.y + v.y)

    def __sub__(self, v):
        return vector(self.x - v.x, self.y - v.y)

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

    def astuple(self):
        return (int(self.x), int(self.y))


class board:

    def __init__(self, posi, len, lon, w, h):
        self.w = w
        self.h = h
        self.dim = [len, lon]
        self.holes = []  # all the holes (just for visualization)
        self.circles = []
        for i in range(w):
            for j in range(h):
                self.circles.append([posi + vector(i * len / w + len / w / 2, j * lon / h + lon / h / 2), (0, 0, 0)])

    def set(self, i, j, col):
        self.circles[self.h * i + j][1] = col

    def clear(self):
        for i in range(self.w):
            for j in range(self.h):
                self.circles[self.h * i + j][1] = (0, 0, 0)

    def draw(self, draw, screen):
        rad = int(min(pfill * self.dim[0] / self.w, pfill * self.dim[1] / self.h) / 2)
        for c, col in self.circles:
            draw.circle(screen, col, c.astuple(), rad)


class node:

    def __init__(self, up, down, aux):
        self.up = up
        self.down = down
        self.aux = aux

    def __repr__(self):
        return 'u: {} d: {} i: {}   '.format(self.up, self.down, self.aux)


class item:

    def __init__(self, name, left, right):
        self.name = name
        self.left = left
        self.right = right

    def __eq__(self, other):
        return other == self.name

    def __repr__(self):
        return 'n: {} l: {} r: {}   '.format(self.name, self.left, self.right)


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


colormap = {'w0': (255,0,255), 'w1': (0,0,255), 'w2': (255,127,0), 'w3': (127,220,255), 'w4': (255,0,0), 'w5': (153,153,153),
'w6': (255,105,181), 'w7': (0,180,26), 'w8': (.230,193,193), 'w9': (0, 255, 0), 'w10': (255, 255, 0), 'w11': (255,180,180)}

b = board(vector(0, 0), 640, 480, 11, 5)


def create_board_setup(soln):
    b.clear()
    for option in soln:
        col = colormap[option[0]]
        for tile in option[1:]:
            i, j = tile.split(',')
            x = int(i)
            y = int(j)
            b.set(x, y, col)


def selp(nodes, items, options, partial_soln):
    if items[0].right == 0:
        yield [options[xl] for xl in partial_soln]
        return
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
        part = partial_soln + [get_index(nodes, xl)]
        # yield [options[xl] for xl in part]
        yield from selp(nodes, items, options, part)
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


def parse_file(file_loc):
    with open(file_loc, 'r') as file:
        itms = ['_'] + file.readline().strip().split(' ')
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

        for line in file.readlines():
            first_in_row = 0
            p += 1
            options.append(line.strip().split(' '))
            for opt in options[-1]:
                i = items.index(opt)
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


def solve(file_loc):
    nodes, items, options = parse_file(file_loc)
    yield from selp(nodes, items, options, [])


if __name__ == '__main__':
    #solve('kan.txt')
    run = 1
    gen = solve('kan.txt')
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = 0
        screen.fill((255, 255, 255))
        if run == 1:
            create_board_setup(next(gen))
            run += 1
        b.draw(pygame.draw, screen)
        pygame.display.flip()
    pygame.display.quit()

