import random

Clock.bpm = random.randint(70,180)

scales = ['aeolian', 'chinese', 'chromatic', 'custom', 'default', 'diminished', 'dorian',
'dorian2', 'egyptian', 'freq', 'harmonicMajor', 'harmonicMinor', 'indian',
'justMajor', 'justMinor', 'locrian', 'locrianMajor', 'lydian', 'lydianMinor',
'major', 'majorPentatonic', 'melodicMajor', 'melodicMinor', 'minor',
'minorPentatonic', 'mixolydian', 'phrygian', 'prometheus', 'romanianMinor', 'yu',
'zhi']

Scale.default = random.choice(scales)
Root.default.set(random.randint(0,7))


melody_instruments = [lazer, charm, bell, gong, viola, pluck, blip, orient, marimba, twang, karp, arpy, nylon, sitar, star, pads, pasha, sinepad]
melody_instrument = random.choice(melody_instruments)

chord_instruments = [varsaw, scatter, quin, spark, ripple, creep, zap, bug, pulse, saw, donk, squish, swell, razz, prophet, keys]
chord_instrument = random.choice(chord_instruments)

ambient_soft_instruments = [crunch, soprano, scratch, klank, feel, glass, soft, ambi, space]
ambient_soft_instrument = random.choice(ambient_soft_instruments)

ambient_noise_instruments = [noise, growl, rave, fuzz, snick, dub]
ambient_noise_instrument = random.choice(ambient_noise_instruments)

bass_instruments = [dab, bass, dirt, jbass, sawbass, dbass]
bass_instrument = random.choice(bass_instruments)

n_chords = 4

chord_list = list()

for i in range(n_chords):
    r = random.randint(0,7)
    chord_list.append((r,r+2,r+4))

print(chord_list)

c1 >> chord_instrument(chord_list)

n_melody = 16

melody_list = list()

for i in range(n_melody):
    r = random.randint(0,7)
    melody_list.append(r)

m1 >> melody_instrument(melody_list, dur=1/2, amp = 0.7)


n_bass = 4

bass_list = list()

for i in range(n_bass):
    r = random.randint(0,7)
    bass_list.append(r)

b1 >> bass_instrument(bass_list, dur = 2, amp = 0.5)


r = random.randint(0,7)
a1 >> ambient_soft_instrument(r, dur = 4, amp = 0.7)

d1 >> play(".-ox")