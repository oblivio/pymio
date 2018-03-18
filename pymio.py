import sys
import subprocess
import pytube
import yaml
from googlesearch import search
from flask import request
import urllib.parse as urlparse
import json
from flask import render_template,send_from_directory

class VideoDownloader:
    def init(self):
        vd.read_yaml()
    def read_yaml(self):
        with open('config.yaml') as config:
            pymio = yaml.safe_load(config)
            for vid in pymio:
                artist=pymio[vid]['artist'] if 'artist' in pymio[vid] else ''
                album=pymio[vid]['album'] if 'album' in pymio[vid] else ''
                title=pymio[vid]['title'] if 'title' in pymio[vid] else ''
                genre=pymio[vid]['genre'] if 'genre' in pymio[vid] else ''
                description=pymio[vid]['description'] if 'description' in pymio[vid] else ''
                year=pymio[vid]['year'] if 'year' in pymio[vid] else ''
                print("Downloading...",vid,artist,album,title)
                self.delete_mp3(vid)
                self.download_video(vid, title, artist, album, genre, description, year)

    def download_video(self,video_id, title, artist, album, genre, description, year):
        downloads_dir = 'downloads'
        yt = pytube.YouTube('http://youtube.com/watch?v='+video_id)
        yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(downloads_dir)
        subprocess.call([
            "ffmpeg",
            "-i",
            downloads_dir+"/"+yt.title+".mp4",
            "-metadata",
            "title="+title,
            "-metadata",
            "artist="+artist,
            "-metadata",
            "album="+album,
            "-metadata",
            "genre="+genre,
            "-metadata",
            "description="+description,
            "-metadata",
            "year="+year,
            downloads_dir+"/"+video_id+".mp3",
            ])
        self.delete_video(video_id,downloads_dir,yt)
    def delete_video(self,video_id,downloads_dir,yt):
        subprocess.call([
            "rm",
            "-rf",
            downloads_dir+"/"+yt.title+".mp4",
        ])
    def delete_mp3(self,video_id):
        downloads_dir = 'downloads'
        subprocess.call([
            "rm",
            "-rf",
            downloads_dir+"/"+video_id+".mp3",
        ])

    def search_google(self,query_string):
        urls = []
        for url in search('youtube.com watch?=v ' + query_string, stop=1):
            print(url)
            urls.append(url)
        return urls

vd = VideoDownloader()

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app,send_wildcard=True)#should probably be stricter :)

@app.route("/download_videos")
def download_videos():
    vd.init()
    return json.dumps( {"action":"download","result":"success"} )

@app.route("/set_yaml")
def set_yaml():
    URL = request.url
    parsed_url = urlparse.urlparse(URL)
    tmpDict = (urlparse.parse_qs(parsed_url.query))
    yamlDict = {}
    yamlDict[tmpDict['vid_id'][0]] = {}

    for key in tmpDict:
        yamlDict[tmpDict['vid_id'][0]][key]=tmpDict[key]

    with open('config.yaml') as config:
        pymio = yaml.safe_load(config)
        if not pymio:
            pymio = {}

        pymio[tmpDict['vid_id'][0]] = yamlDict[tmpDict['vid_id'][0]]
        if 'del' in tmpDict:
            newData = {}
            for key in pymio:
                if key != tmpDict['vid_id'][0]:
                    newData[key] = pymio[key]
            pymio = newData
        ff = open('config.yaml', 'w+')
        yaml.dump(pymio, ff, allow_unicode=True)

    response = {}
    response['action']="modify-yaml"
    response['result']="success"

    return json.dumps(response)

@app.route("/get_yaml")
def get_yaml():
    with open('config.yaml') as config:
        pymio = yaml.safe_load(config)
        for vid in pymio:
            print(pymio[vid])

    return json.dumps(pymio)

@app.route("/search")
def google_search():
    URL = request.url
    parsed_url = urlparse.urlparse(URL)
    tmpDict = (urlparse.parse_qs(parsed_url.query))
    video_urls = vd.search_google(tmpDict['q'][0])

    search_results = {}
    search_results['results'] = []

    for url in video_urls:
        tParseURL = urlparse.urlparse(url)
        temporaryDict = (urlparse.parse_qs(tParseURL.query))
        if('v' in temporaryDict):
            search_results['results'].append(temporaryDict['v'][0])

    return json.dumps(search_results)

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/css/<path:path>')
def send_js(path):
    return send_from_directory('css', path)
