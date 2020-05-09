import json
import subprocess

CONFIG_PARAMETERS = {"num_instruments": 3, "chord_duration": 2, "chord_number": 4, "percussion_interval": 2,
                    "bpm": 120, "root": 0, "song_duration": 12, "melody_possibilities": [1/4,1/2,1,2]}


with open('config/params.json', 'w') as outfile:
    json.dump(CONFIG_PARAMETERS, outfile)

subprocess.check_call(['sudo', './foxsamply', '-f', 'markov.py', '-s', str(CONFIG_PARAMETERS["song_duration"] + 1), '-o', 'output/twitter/music'])


import numpy as np
import mayavi.mlab as mlab
import moviepy.editor as mpy
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import gizeh

mlab.options.offscreen = True

# VISUALIZATIONS TAKEN FROM: 
# http://zulko.github.io/blog/2014/11/29/data-animations-with-python-and-moviepy/
# https://zulko.github.io/blog/2014/09/20/vector-animations-with-python/


W,H = 1024,1024
NFACES, R, NSQUARES, DURATION = 5, CONFIG_PARAMETERS["bpm"] / 60,  100, CONFIG_PARAMETERS["bpm"] / 60

def hsl_to_rgb(h, s, l):
    def hue_to_rgb(p, q, t):
        t += 1 if t < 0 else 0
        t -= 1 if t > 1 else 0
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: p + (q - p) * (2/3 - t) * 6
        return p

    if s == 0:
        r, g, b = l, l, l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)

    return r, g, b

# sin function: f(x) = amplitude * sin(period * (x + phase_shift)) + vertical_shift
amplitude = CONFIG_PARAMETERS["percussion_interval"] / 16
phase_shift = amplitude + 1
vertical_shift = amplitude + 0.2
frequency = CONFIG_PARAMETERS["bpm"] / 60 / 2

def half(t, side="left"):
    points = list(gizeh.geometry.polar_polygon(NFACES, amplitude * np.sin(2 * np.pi * frequency * t + phase_shift) + vertical_shift, NSQUARES))
    ipoint = 0 if side=="left" else int(NSQUARES/2)
    points = (points[ipoint:]+points[:ipoint])[::-1]

    surface = gizeh.Surface(W,H)
    for (r, th, d) in points:
        center = W*(0.5+gizeh.polar2cart(r,th))
        angle = -(6*np.pi*d + t*np.pi/DURATION)
        color= hsl_to_rgb((2*d+t/DURATION)%1,.5,.5)
        square = gizeh.square(l=0.17*W, xy= center, angle=angle,
                   fill=color, stroke_width= 0.005*W, stroke=(1,1,1))
        square.draw(surface)
    im = surface.get_npimage()
    return (im[:,:int(W/2)] if (side=="left") else im[:,int(W/2):])


def make_frame(t):
    return np.hstack([half(t,"left"),half(t,"right")])


'''
# PLAVE WAVE

#1 == 60bpm
gif_duration= CONFIG_PARAMETERS["bpm"] / 60

fig_myv = mlab.figure(size=(220,220), bgcolor=(1,1,1))
X, Y = np.linspace(-2,2,200), np.linspace(-2,2,200)
XX, YY = np.meshgrid(X,Y)
ZZ = lambda d: np.sinc(XX**2+YY**2)+np.sin(XX+d)

def make_frame(t):
    mlab.clf()
    mlab.mesh(YY,XX,ZZ(2*np.pi*t/gif_duration), figure=fig_myv, colormap="bone")
    return mlab.screenshot(antialiased=True)
'''

'''
# WIREFRAME MESH

#1 == 60bpm
gif_duration= CONFIG_PARAMETERS["bpm"] / 60

fig = mlab.figure(size=(500, 500), bgcolor=(1,1,1))

u = np.linspace(0,2*np.pi,100)
xx,yy,zz = np.cos(u), np.sin(3*u), np.sin(u) # Points
l = mlab.plot3d(xx,yy,zz, representation="wireframe", tube_sides=5,
                line_width=.5, tube_radius=0.2, figure=fig)

def make_frame(t):
    """ Generates and returns the frame for time t. """
    y = np.sin(3*u)*(0.2+0.5*np.cos(2*np.pi*t/gif_duration))
    l.mlab_source.set(y = y)
    mlab.view(azimuth= 360*t/gif_duration, distance=9)
    return mlab.screenshot(antialiased=True)
'''

clip = mpy.VideoClip(make_frame, duration=CONFIG_PARAMETERS["song_duration"] + 1)

clip.write_videofile("output/twitter/video.mp4", audio="output/twitter/music.mp3", fps=15)

ffmpeg_extract_subclip(clip, 1, CONFIG_PARAMETERS["song_duration"] + 1, targetname="test.mp4")

print("FINISH")