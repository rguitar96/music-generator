import random
import csv
import numpy as np
import json

with open('config/params.json', 'r') as openfile:
    CONFIG_PARAMETERS = json.load(openfile)

MAX_NUM_INSTRUMENTS = 5

#TODO: parametrize
NUM_INSTRUMENTS = CONFIG_PARAMETERS["num_instruments"]
CHORD_DURATION = CONFIG_PARAMETERS["chord_duration"]
CHORD_NUMBER = CONFIG_PARAMETERS["chord_number"]
PERCUSSION_INTERVAL = CONFIG_PARAMETERS["percussion_interval"]
Clock.bpm = CONFIG_PARAMETERS["bpm"]

scales = ['aeolian', 'chinese', 'chromatic', 'custom', 'default', 'diminished', 'dorian',
'dorian2', 'egyptian', 'freq', 'harmonicMajor', 'harmonicMinor', 'indian',
'justMajor', 'justMinor', 'locrian', 'locrianMajor', 'lydian', 'lydianMinor',
'major', 'majorPentatonic', 'melodicMajor', 'melodicMinor', 'minor',
'minorPentatonic', 'mixolydian', 'phrygian', 'prometheus', 'romanianMinor', 'yu',
'zhi']

#TODO: parametrize
Scale.default = random.choice(scales)
Root.default.set(CONFIG_PARAMETERS["root"])

instrument_list = ["melody", "bass", "chord", "ambient", "percussion"]

for i in range(NUM_INSTRUMENTS-MAX_NUM_INSTRUMENTS):
    instrument_list.remove(random.choice(instrument_list))

instrument_intensities = dict()
for instrument in instrument_list:
    instrument_intensities[instrument] = random.randint(5, 10) / 10

norm_bigram_matrix = list()
file_name = "four_chord_songs/coocurrence.csv"
with open(file_name, 'r') as f:
    reader = csv.reader(f)
    
    for row in reader:
        norm_bigram_matrix.append([float(num) for num in row])

for row in norm_bigram_matrix:
    if sum(row) == 0:
        row[0] = 0.5
        row[5] = 0.5


melody_instruments = [lazer, charm, bell, gong, viola, pluck, blip, orient, marimba, karp, arpy, nylon, sitar, star, pads, pasha, sinepad]
melody_instrument = None
if "melody" in instrument_list:
    melody_instrument = random.choice(melody_instruments)

chord_instruments = [varsaw, scatter, quin, spark, ripple, creep, zap, bug, pulse, saw, donk, squish, swell, razz, prophet, keys]
chord_instrument = None
if "chord" in instrument_list:
    chord_instrument = random.choice(chord_instruments)

ambient_soft_instruments = [crunch, soprano, scratch, klank, feel, glass, soft, ambi, space]
ambient_soft_instrument = None
if "ambient" in instrument_list:
    ambient_soft_instrument = random.choice(ambient_soft_instruments)

ambient_noise_instruments = [noise, growl, rave, fuzz, snick, dub, dab, twang]
ambient_noise_instrument = random.choice(ambient_noise_instruments)

# "bass" conflicts with "v" in percussion
bass_instruments = [dirt, jbass, sawbass, dbass]

bass_instrument = None
if "bass" in instrument_list:
    bass_instrument = random.choice(bass_instruments)

n_chords = CHORD_NUMBER

chord_list = list()

first_chord = random.randint(0,7)
chord_list.append((first_chord, first_chord+2, first_chord+4))

for i in range(n_chords-1):
    r = np.random.choice(range(0,7), p=norm_bigram_matrix[chord_list[-1][0]])
    chord_list.append((r,r+2,r+4))


melody_list = list()

melody_durations = list()
duration = 0
possibilities = CONFIG_PARAMETERS["melody_possibilities"]

while (len(possibilities) > 0):
    pos = [0,1,2,3,4,5,6]
    pos.remove((chord_list[int((duration % 8)/2)][0]+3) % 7)
    
    melody_list.append(np.random.choice(pos))
    
    melody_list.append(random.randint(0,7))
    d = np.random.choice(possibilities)
    melody_durations.append(d)
    duration = duration + d
    possibilities = [item for item in possibilities if duration+item <= CHORD_DURATION*CHORD_NUMBER]

duration = 0
while (len(possibilities) > 0):
    pos = [0,1,2,3,4,5,6]
    pos.remove((chord_list[int((duration % 8)/2)][0]+3) % 7)
    
    melody_list.append(np.random.choice(pos))
    
    melody_list.append(random.randint(0,7))
    d = np.random.choice(possibilities)
    melody_durations.append(d)
    duration = duration + d
    possibilities = [item for item in possibilities if duration+item <= CHORD_DURATION*CHORD_NUMBER]


n_bass = CHORD_NUMBER

bass_list = list()

bass_pattern = list()
bass_durations = list()

for chord in chord_list:
    possibilities = [1/2,1,2]
    duration = 0
    bass_list.append(chord[0])
    d = np.random.choice(possibilities)
    bass_durations.append(d)
    duration = duration + d
    possibilities = [item for item in possibilities if duration+item <= CHORD_DURATION]
    while (len(possibilities) > 0):
        bass_list.append(random.randint(0,7))
        d = np.random.choice(possibilities)
        bass_durations.append(d)
        duration = duration + d
        possibilities = [item for item in possibilities if duration+item <= CHORD_DURATION]



r = chord_list[0][0]


percussion_instruments = ["v", "-", "o", "x", "d", "*"]

if (bass_instrument != None):
    percussion_instruments.remove("v")

perc_str = ""

for i in range(16):
    if i % PERCUSSION_INTERVAL == 0:
        perc_str = perc_str + "{" + random.choice(percussion_instruments) + random.choice(percussion_instruments) + "- }"
    elif i % PERCUSSION_INTERVAL == PERCUSSION_INTERVAL - 1:
        perc_str = perc_str + "{" + random.choice(percussion_instruments) + "-}"
    else:
        perc_str = perc_str + "{- }"



print("CHORD LIST: ", chord_list)
print("BASS LIST: ", bass_list)
print("BASS DURATIONS: ", bass_durations)
print("MELODY_LIST: ", melody_list)
print("MELODY_DURATIONS: ", melody_durations)


print("CHORD INSTRUMENT: ", chord_instrument)
print("BASS INSTRUMENT: ", bass_instrument)
print("MELODY INSTRUMENT: ", melody_instrument)
print("AMBIENT INSTRUMENT: ", ambient_soft_instrument)
print("PERCUSSION: ", perc_str)

if (chord_instrument != None):
    c1 >> chord_instrument(chord_list, dur=CHORD_DURATION, amp=instrument_intensities["chord"])
if (melody_instrument != None):
    m1 >> melody_instrument(melody_list, dur=melody_durations, amp = instrument_intensities["melody"])
if (bass_instrument != None):
    b1 >> bass_instrument(bass_list, dur = bass_durations, amp = instrument_intensities["bass"])
if (ambient_soft_instrument != None):
    a1 >> ambient_soft_instrument(r, dur = CHORD_DURATION*2, amp = instrument_intensities["ambient"])
if (perc_str != ""):
    d1 >> play(perc_str, sample=0)