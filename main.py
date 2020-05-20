import json
import subprocess
import numpy as np
#import mayavi.mlab as mlab
import moviepy.editor as mpy
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import gizeh
from TwitterAPI import TwitterAPI
import time, os, json, sys

#from credentials import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

#mlab.options.offscreen = True


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

def check_status(request):
    print(request.text)
    sys.stdout.flush()
    if request.status_code < 200 or request.status_code > 299:
        print(request.status_code)
        sys.stdout.flush()
        print(request.text)
        sys.stdout.flush()
        sys.exit(0)

def upload_video(filename):
    # Upload a video
    bytes_sent = 0
    total_bytes = os.path.getsize(filename)
    file = open(filename, 'rb')

    # Initial request
    request = api.request('media/upload', {'command':'INIT', 'media_type':'video/mp4', 'total_bytes':total_bytes, 'media_category': 'tweet_video'})
    check_status(request)
    media_id = request.json()['media_id']
    segment_id = 0

    # Chunk and upload video
    while bytes_sent < total_bytes:
        chunk = file.read(4*1024*1024)

        request = api.request('media/upload', {'command':'APPEND', 'media_id':media_id, 'segment_index':segment_id}, {'media':chunk})
        check_status(request)

        segment_id = segment_id + 1
        bytes_sent = file.tell()

        print('[' + str(total_bytes) + ']', str(bytes_sent))
        sys.stdout.flush()

    request = api.request('media/upload', {'command':'FINALIZE', 'media_id':media_id})

    check_status(request)
    while request.json()['processing_info']['state'] in ['pending','in_progress']:
        time.sleep(1)
        request = api.request('media/upload', {'command':'FINALIZE', 'media_id':media_id})
        check_status(request)

    return request


# VISUALIZATIONS TAKEN FROM: 
# http://zulko.github.io/blog/2014/11/29/data-animations-with-python-and-moviepy/
# https://zulko.github.io/blog/2014/09/20/vector-animations-with-python/

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

CONFIG_PARAMETERS = {"num_instruments": 3, "chord_duration": 2, "chord_number": 4, "percussion_interval": 2,
                    "bpm": 120, "root": 0, "song_duration": 12, "melody_possibilities": [1/4,1/2,1,2]}


with open('config/params.json', 'w') as outfile:
    json.dump(CONFIG_PARAMETERS, outfile)

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_KEY = os.environ['ACCESS_KEY']
ACCESS_SECRET = os.environ['ACCESS_SECRET']

api = TwitterAPI(
    CONSUMER_KEY,
    CONSUMER_SECRET,
    ACCESS_KEY,
    ACCESS_SECRET
)

#since_id = 1
since_id = int(os.environ['LAST_ID'])
while True:
    print("new try")
    sys.stdout.flush()
    new_since_id = since_id
    mentions = api.request('statuses/mentions_timeline', {'since_id': new_since_id}).json()
    mentions = sorted(mentions, key=lambda k:k['id'])
    if mentions:
        print("mentions")
        sys.stdout.flush()
        for tweet in mentions:
            print("tweet:")
            sys.stdout.flush()
            tweet_text = tweet['text'].encode('ascii', 'ignore')
            print(tweet_text)
            sys.stdout.flush()

            new_since_id = max(tweet['id'], new_since_id)
            
            user = tweet['user']

            if user['screen_name'] != "musgenbot":
                print("funca")
                sys.stdout.flush()
                start_status = "Just for you!"
                #start_post = api.request('statuses/update', {'status': start_status, 'in_reply_to_status_id': tweet['id'], 'auto_populate_reply_metadata': True})
                #print(start_post.json())

                # *** VIDEO GENERATION ***
                subprocess.check_call(['./foxsamply', '-f', 'markov.py', '-s', str(CONFIG_PARAMETERS["song_duration"] + 1), '-o', 'output/twitter/music'])

                W,H = 1024,1024
                NFACES, R, NSQUARES, DURATION = 5, CONFIG_PARAMETERS["bpm"] / 60,  100, CONFIG_PARAMETERS["bpm"] / 60

                # sin function: f(x) = amplitude * sin(period * (x + phase_shift)) + vertical_shift
                amplitude = CONFIG_PARAMETERS["percussion_interval"] / 16
                phase_shift = amplitude + 1
                vertical_shift = amplitude + 0.2
                frequency = CONFIG_PARAMETERS["bpm"] / 60 / 2


                clip = mpy.VideoClip(make_frame, duration=CONFIG_PARAMETERS["song_duration"] + 1)

                clip = clip.set_audio(mpy.AudioFileClip("output/twitter/music.mp3"))

                clip.write_videofile("output/twitter/video.mp4", fps=10, temp_audiofile="output/twitter/temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")

                ffmpeg_extract_subclip("output/twitter/video.mp4", 1, CONFIG_PARAMETERS["song_duration"] + 1, targetname="output/twitter/final_video.mp4")
                time.sleep(2)
                # *** END OF VIDEO GENERATION ***

                media_upload = upload_video("output/twitter/final_video.mp4")
                status_pick = 'video'
                post = api.request('statuses/update', {'status': start_status, 'in_reply_to_status_id': tweet['id'], 
                        'auto_populate_reply_metadata': True, 'media_ids': media_upload.json()['media_id']})
                
                time.sleep(5)
    since_id = new_since_id
    os.environ['LAST_ID'] = str(since_id)

    time.sleep(5)
    

'''
# *** VIDEO GENERATION ***
subprocess.check_call(['sudo', './foxsamply', '-f', 'markov.py', '-s', str(CONFIG_PARAMETERS["song_duration"] + 1), '-o', 'output/twitter/music'])

W,H = 1024,1024
NFACES, R, NSQUARES, DURATION = 5, CONFIG_PARAMETERS["bpm"] / 60,  100, CONFIG_PARAMETERS["bpm"] / 60

# sin function: f(x) = amplitude * sin(period * (x + phase_shift)) + vertical_shift
amplitude = CONFIG_PARAMETERS["percussion_interval"] / 16
phase_shift = amplitude + 1
vertical_shift = amplitude + 0.2
frequency = CONFIG_PARAMETERS["bpm"] / 60 / 2


clip = mpy.VideoClip(make_frame, duration=CONFIG_PARAMETERS["song_duration"] + 1)

clip = clip.set_audio(mpy.AudioFileClip("output/twitter/music.mp3"))

clip.write_videofile("output/twitter/video.mp4", fps=10, temp_audiofile="output/twitter/temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")

ffmpeg_extract_subclip("output/twitter/video.mp4", 1, CONFIG_PARAMETERS["song_duration"] + 1, targetname="output/twitter/final_video.mp4")
time.sleep(2)
# *** END OF VIDEO GENERATION ***

media_upload = upload_video("output/twitter/final_video.mp4")
status_pick = 'video'
post = api.request('statuses/update', {'status': start_status, 'in_reply_to_status_id': tweet['id'], 
                        'auto_populate_reply_metadata': True, 'media_ids': media_upload.json()['media_id']})
'''
    



print("FINISH\n")
sys.stdout.flush()
