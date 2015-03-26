#Sammie

###Requirement
xmms2, https://xmms2.org/wiki/Main_Page
python libs: youtube_dl, flask, Flash-cache
###Installation
```sh
$ sudo apt-get install xmms2-core xmms2 xmms2-plugin-all
$ sudo pip install flask Flask-Cache youtube-dl
```
### Usage
```sh
$ xmms2-launcher #Start the daemon
$ python sammie.py #listen on 0.0.0.0:5000
```

