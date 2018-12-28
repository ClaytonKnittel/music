

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


def parse_file(file_loc):
    with open(file_loc, 'r') as file:
        itms = ['_'] + file.readline().strip().split(' ')
        items = [item(i, loc - 1, loc + 1) for i, loc in zip(itms, range(1, len(itms) + 1))]
        items[0].left = len(items) - 1
        items[-1].right = 0
        nodes = [node(x, x, 0) for x in range(len(itms))]
        p = len(nodes)

        first_in_row = 0
        nodes.append(node(first_in_row, 0, 0))
        last_spacer = nodes[-1]
        num_spacers = 1

        for line in file.readlines():
            first_in_row = 0
            p += 1
            for opt in line.strip().split(' '):
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
        return items, nodes


def hide(nodes, p):
    q = p + 1
    while q != p:
        x = nodes[q].top
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
        x = nodes[q].top
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


def selp(nodes, items, l):
    pass


def solve(file_loc):
    items, nodes = parse_file('inpt.txt')


if __name__ == '__main__':
    items, nodes = parse_file('inpt.txt')
    for i, l in enumerate(nodes):
        print(i, l)

