import requests
from threading import Timer
import logging
import time
import json
from six.moves import input
from glob import glob
import livejson
from moviepy.editor import ImageSequenceClip
import os

"""
cams.json Docs


Each entry consists of a URL, Detetion Type , and finally a FPS (For end of day storage video)

Valid entries for type are as follows.


max-age which uses the max-age argument of the Cache-Control tag in the header to wait.
etag which uses the ETag argument in the header to decide if it is needed to download.
max-age-etag uses both ETag and max-age methods. (For those stuborn URLS)

Example

{'cam1':{'url':'http://example.com','type':'max-age','fps':10}}

"""

LogLevel = 20


class MaxAgeDownload(object):
    def __init__(self, url,name):
        logging.getLogger(name).setLevel(LogLevel)
        self._timer     = None
        self.url        = url
        self.is_running = False
        self.name = name
        self.maxage = 1
        self._timer = Timer(self.maxage, self._run)
        self._timer.setName(self.name)

    def _run(self):
        self.is_running = False
        rep = requests.get(self.url,stream=True)
        logging.getLogger(self.name).info("Downloading new Image.")
        self.maxage = int(rep.headers["Cache-Control"].split("max-age=")[1].split(",")[0]) #Get the max-age using some hacky split strings
        self.start()
        img = open(self.name+"/"+str(int(time.time()))+".jpg","wb+")
        img.write(rep.raw.read())
        img.close()

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.maxage, self._run)
            self._timer.setName(self.name)
            self._timer.start()
            self.is_running = True
            
    def stop(self):
        self._timer.cancel()
        self.is_running = False
        
class ETagDownload(object):
    def __init__(self, url,name):
        logging.getLogger(name).setLevel(LogLevel)
        self._timer     = None
        self.url        = url
        self.is_running = False
        self.name = name
        self.ETag = ""
        self._timer = Timer(1, self._run)
        self._timer.setName(self.name)

    def _run(self):
        self.is_running = False
        rep = requests.get(self.url,stream=True,headers={"If-None-Match":self.ETag})
        
        if rep.status_code == 200:
            logging.getLogger(self.name).info("Downloading new Image.")
            self.ETag = rep.headers["ETag"]
            img = open(self.name+"/"+str(int(time.time()))+".jpg","wb+")
            img.write(rep.raw.read())
            img.close()
        self.start()

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._timer = Timer(60, self._run)
            self._timer.setName(self.name)
            self._timer.start()
            
            
    def stop(self):
        self._timer.cancel()
        self.is_running = False       

class MaxAgeETagDownload(object):
    def __init__(self, url,name):
        logging.getLogger(name).setLevel(LogLevel)
        self._timer     = None
        self.url        = url
        self.is_running = False
        self.name = name
        self.etag = ""
        self.maxage = 1
        self._timer = Timer(self.maxage, self._run)
        self._timer.setName(self.name)

    def _run(self):
        self.is_running = False
        rep = requests.get(self.url,stream=True)
        logging.getLogger(self.name).info("Downloading new Image.")
        self.maxage = int(rep.headers["Cache-Control"].split("max-age=")[1].split(",")[0]) #Get the max-age using some hacky split strings
        self.start()
        if not self.etag == rep.headers["ETag"]:
            img = open(self.name+"/"+str(int(time.time()))+".jpg","wb+")
            img.write(rep.raw.read())
            img.close()
        self.etag = rep.headers["ETag"]

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.maxage, self._run)
            self._timer.setName(self.name)
            self._timer.start()
            self.is_running = True
            
    def stop(self):
        self._timer.cancel()
        self.is_running = False
        

    
def main():
    logging.basicConfig(format = '%(asctime)s [%(name)s] [%(levelname)s] %(message)s')
    log = logging.getLogger("TimeLapse")
    log.setLevel(LogLevel)
    log.info("TimeLapse Starting!")
    
    #Read in the Cameras!
    camfile = open("cams.json")
    cameras = json.load(camfile)
    camfile.close()
    
    for x in cameras.keys():
        try:
            os.mkdir(x)
            os.mkdir(x+"-mp4")
        except Exception as e:
            log.error("Could not create folder "+x+"!")
            log.error("Exception: "+str(e))
        log.info("Added Camera "+x)
        if cameras[x]["type"] == "etag":
            cameras[x]["instance"] = ETagDownload(cameras[x]["url"],x)
        if cameras[x]["type"] == "max-age":
            cameras[x]["instance"] = MaxAgeDownload(cameras[x]["url"],x) 
        if cameras[x]["type"] == "max-age-etag":
            cameras[x]["instance"] = MaxAgeETagDownload(cameras[x]["url"],x)
        cameras[x]["instance"].start()
    
    while True:
        command = input(">")
        if command == "list-cams":
            for x in cameras.keys():
                log.info(x +": Running? "+str(cameras[x]["instance"].is_running))
        elif command.startswith("stopcam"):
            cam = command.split(" ")[1]
            if not cam in cameras.keys():
                log.error("Invalid Camera name")
            else:
                log.info("Camera "+cam+" stopped!")
                cameras[cam]["instance"].stop()
                
        elif command.startswith("startcam"):
            cam = command.split(" ")[1]
            if not cam in cameras.keys():
                log.error("Invalid Camera name")
            else:
                log.info("Camera "+cam+" started!")
                cameras[cam]["instance"].start()
        elif command.startswith("save"):
            for x in cameras.keys():
                cameras[x]["instance"].stop()
            log.info("All Camers Stopped!")  
            for x in cameras.keys():
                log.info("Saving "+x)
                data = livejson.File(x+"-mp4/cat.json")
                t = str(int(time.time()))
                q = ImageSequenceClip(x,fps=cameras[x]["fps"])
                q.write_videofile(x+"-mp4/"+t+".mp4")
                data[t]=glob(x+"/*.jpg")
                for y in glob(x+"/*.jpg"):
                    os.remove(y)
            log.info("All Cameras started!")
            for x in cameras.keys():
                cameras[x]["instance"].start()
        elif command.startswith("stopcams"):
            for x in cameras.keys():
                cameras[x]["instance"].stop()
            log.info("All Camers Stopped!")  
        elif command.startswith("startcams"):
            for x in cameras.keys():
                cameras[x]["instance"].start()
            log.info("All Camers Stopped!")  
        elif command == "stop":
            log.info("Stopping all cameras and halting!")
            for x in cameras.keys():
                cameras[x]["instance"].stop()
            break
        elif command == "help": 
            log.info("help: Shows this.")
            log.info("list-cams: Lists the current cameras.")
            log.info("stopcam: Stops a cameras recording.")
            log.info("startcam: Starts a camera recording.")
            log.info("stop: Stops this program.")
       
        else:
            log.error("Command not found! " +command)
            
            
if __name__ == "__main__":
    main()