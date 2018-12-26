from music21 import note, converter, duration, chord, dynamics, stream, clef, meter, metadata

# c = converter.parse('/users/claytonknittel/downloads/Beethoven.musicxml')

# n = note.Note('C4')
# n.duration.type = 'half'
# n.show()

# melody = converter.parse('tinynotation: 3/4 c4 d8 f g16 a g f#')
# melody.show()

# f = note.Note('F5')
# g = note.Chord('F5', 'F6')

# dy = dynamics.Dynamic('p')
# dy.offset = 2.0
# c[3][1].insert(dy)
# for el in c.recurse().getElementsByClass('ChordSymbol'):
#     c.remove(el, recurse=True)

# c.show('text')
# c.show()

# c.write('musicxml', '/users/claytonknittel/downloads/Beethoven.musicxml')

s = stream.Score()

s.insert(0, metadata.Metadata())
s.metadata.title = 'score'
s.metadata.composer = 'a computer'


p1 = stream.Part()
p1.offset = 0
p1.id = 'Part'

t = meter.TimeSignature('3/4')
p1.insert(0, t)

cl = clef.TrebleClef()
cl.priority = -1
p1.insert(0, cl)

p1.append(note.Note('F4', duration=duration.Duration(2)))
p1.append(note.Note('E4', duration=duration.Duration(1)))

s.insert(0, p1)


p2 = stream.Part()
p2.insert(0, metadata.Metadata())
p2.metadata.title = 'Part 2'

p2.insert(0, t)
p2.insert(clef.BassClef())

p2.append(note.Note('C2'))
p2.append(note.Note('D2'))
p2.append(note.Note('E2', duration=duration.Duration(.5)))
p2.append(note.Note('G2', duration=duration.Duration(.25)))
p2.append(note.Note('A2', duration=duration.Duration(.25)))

s.insert(0, p2)


s.show()

# print(cmaj.commonName)

# s.show()

# bach = corpus.parse('bach/bwv57.8')
#
# bach.show('text')

# s.show()
