#!/usr/bin/env python

import sys, os, pdb, json
import BaseHTTPServer
import youtube_dl
import xml.etree.ElementTree as ET
import re
import requests
from flask import Flask, request, Response
from flask import render_template
from flask.ext.cache import Cache
from flask import current_app
app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
app.cache = Cache(app)

AUDIOS_DIR = '/tmp' # auto trash every downloaded files
#mp3 zing
class Zing:
    def __init__(self, url):
        self.url = url
        matches = re.search(r'http:\/\/(www\.)?mp3\.zing\.vn\/(.*)\/[^>]*\/([^>]*)\.html', url)
        self.ztype = matches.group(2)
        self.zid = matches.group(3)
        self.xmlurl = ''
        self.title = ''
        self.performer = ''
        self.source = ''

    def fetch(self):
        try:
            res = requests.get(self.url)
            self.xmlurl = re.search(r'xmlURL=(.+?)\&amp\;textad', res.content).group(1)
            xmldoc = ET.fromstring(requests.get(self.xmlurl).content)
            self.title = [e.text.encode('utf-8') for e in xmldoc.iter('title')][0]
            self.performer = [e.text.encode('utf-8') for e in xmldoc.iter('performer')][0]
            self.source = [e.text.encode('utf-8') for e in xmldoc.iter('source')][0]
            with open('%s/%s.mp3' % (AUDIOS_DIR, self.zid), "w") as f:
                f.write(requests.get(self.source).content)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def play(self):
        try:
            os.system('xmms2 add %s/%s.mp3 && xmms2 play' % (AUDIOS_DIR, self.zid))
        except:
            print "Make sure xmms2 is running and nyxmms2 is installed"
            raise


# youtube
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


class Youtube:
    def my_hook(d):
        if d['status'] == 'finished':
            print('Done downloading, now converting ...')
    ydl_opts = {
        'outtmpl': '/tmp/%(id)s.%(ext)s',
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }
    ydl = youtube_dl.YoutubeDL(ydl_opts)

    def __init__(self, url):
        self.url = url

    def fetch(self):
        # youtube
        url = self.url #url go here
        print("Downloading from %s ..." % url)
        with ydl:
            rs = ydl.extract_info(
                    url,
                    )
            if 'entries' in rs: video = rs['entries'][0] # can be playlist or a list of videos
            else: video = rs # just a video

            # record = (video['id'], video['title'], "%s/%s.mp3" % (AUDIOS_DIR, video['id']) )
            # with open('playlist.txt', 'a') as pfile:
            #     pfile.write(record)

            video_url = video['url']
            print(video_url)


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        # maybe pre processing to identify provider #nextfeature
        if current_app.cache.get(request.environ['REMOTE_ADDR']):
            data = { 'error': 'Wait for at least 10 mins'}
        else:
            try:
                song = Zing(request.form['url'])
                song.fetch()
                song.play()
                data = { 'success': True }
                current_app.cache.set(request.environ['REMOTE_ADDR'], 'dolly', timeout=600)
            except Exception, e:
                data = { 'error': str(e).encode('utf-8') }
        # response json
        resp = Response(
                response=json.dumps(data),
                status=200,
                mimetype="application/json")
        return resp

if __name__ == "__main__":
    print("\m/....")
    app.run(host='0.0.0.0', debug=True)
