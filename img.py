from PIL import Image


def rgb_to_hsb(rgb):
    r = rgb[0] / 255
    g = rgb[1] / 255
    b = rgb[2] / 255
    cmax = max([r, g, b])
    cmin = min([r, g, b])
    d = cmax - cmin

    if d == 0:
        h = 0
    elif cmax == r:
        h = 60 * ((g - b) / d % 6)
    elif cmax == g:
        h = 60 * ((b - r) / d + 2)
    else:
        h = 60 * ((r - g) / d + 4)

    if cmax == 0:
        s = 0
    else:
        s = d / cmax

    return (h, s, cmax)


def hsb_to_rgb(hsb):
    c = hsb[2] * hsb[1]
    x = c * (1 - abs((hsb[0] / 60) % 2 - 1))
    m = hsb[2] - c
    which = int(hsb[0] / 60)
    if which == 0:
        r = c
        g = x
        b = 0
    elif which == 1:
        r = x
        g = c
        b = 0
    elif which == 2:
        r = 0
        g = c
        b = x
    elif which == 3:
        r = 0
        g = x
        b = c
    elif which == 4:
        r = x
        g = 0
        b = c
    else:
        r = c
        g = 0
        b = x
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


img = Image.open("/users/claytonknittel/downloads/children-jesus-mary_and_joseph-big_present-presents-gifts-wda1333_low.jpg")
mask = Image.open("/users/claytonknittel/downloads/mask.jpg")
pix = img.load()
mpix = mask.load()

boolmask = []
for i in range(img.size[0]):
    boolmask.append([])
    for j in range(img.size[1]):
        boolmask[-1].append(sum(mpix[i, j]) < 10)


for i in range(250, 400):
    for j in range(250, 343):
        newcol = rgb_to_hsb(pix[i, j])
        newcol2 = (newcol[0], newcol[1], newcol[2] + .1)
        pix[i, j] = hsb_to_rgb(newcol2)


# for i in range(img.size[0]):
#     for j in range(img.size[1]):
#         if boolmask[i][j]:
#             sums = []
#             tdif = 0
#             dif = 1
#             while True:
#                 if i - dif < 0:
#                     break
#                 if not boolmask[i - dif][j]:
#                     sums.append((pix[i - dif, j], dif))
#                     tdif += 1 / dif
#                     break
#                 dif += 1
#
#             dif = 1
#             while True:
#                 if i + dif >= img.size[0]:
#                     break
#                 if not boolmask[i + dif][j]:
#                     sums.append((pix[i + dif, j], dif))
#                     tdif += 1 / dif
#                     break
#                 dif += 1
#
#             dif = 1
#             while True:
#                 if j - dif < 0:
#                     break
#                 if not boolmask[i][j - dif]:
#                     sums.append((pix[i, j - dif], dif))
#                     tdif += 1 / dif
#                     break
#                 dif += 1
#
#             dif = 1
#             while True:
#                 if j + dif >= img.size[1]:
#                     break
#                 if not boolmask[i][j + dif]:
#                     sums.append((pix[i, j + dif], dif))
#                     tdif += 1 / dif
#                     break
#                 dif += 1
#
#             newcol = [0, 0, 0]
#             if tdif > 0:
#                 for c in sums:
#                     newcol[0] += c[0][0] / tdif / c[1]
#                     newcol[1] += c[0][1] / tdif / c[1]
#                     newcol[2] += c[0][2] / tdif / c[1]
#                 pix[i, j] = tuple(int(i) for i in newcol)


def around(w, h, i, j):
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            if i + dx >= 0 and i + dx < w and j + dy >= 0 and j + dy < h:
                if not boolmask[i + dx][j + dy]:
                    yield (i + dx, j + dy)


passed = True and False
passes = 0

while passed:
    passed = False
    passes += 1
    clone = []
    newmask = []
    for i in range(0, img.size[0]):
        clone.append([])
        newmask.append([])
        for j in range(0, img.size[1]):
            clone[-1].append(pix[i, j])
            if boolmask[i][j]:
                total = [0, 0, 0]
                count = 0
                for pt in around(*img.size, i, j):
                    count += 1
                    p = pix[pt[0], pt[1]]
                    total[0] += p[0]
                    total[1] += p[1]
                    total[2] += p[2]
                if count < 2:
                    newmask[-1].append(boolmask[i][j])
                    continue

                passed = True
                total[0] /= count
                total[1] /= count
                total[2] /= count
                # pix[i, j] = tuple(int(i) for i in total)
                clone[-1][-1] = tuple(int(i) for i in total)
                newmask[-1].append(False)
            else:
                newmask[-1].append(boolmask[i][j])

    for i in range(0, img.size[0]):
        for j in range(0, img.size[1]):
            pix[i, j] = clone[i][j]
            boolmask[i][j] = newmask[i][j]


print(passes, 'passes')

img.show()

img.save("/users/claytonknittel/downloads/new.jpg")
img.close()

