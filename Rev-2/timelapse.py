from six.moves.urllib import request
from six.moves import input
from threading import Timer
from PIL import Image
import time
import json

from glob import glob
import os
import datetime
import logging

LogLevel = 20

AnimateTimer = None

def downloadImage(URL,saveLoc):
    url = request.urlopen(URL)
    img = Image.open(url)
    img.save(saveLoc+"/"+str(int(time.time()))+".jpg",optimize=True,progressive=True,quality=60)
    url.close()

class RepeatingDownload(object):
    def __init__(self, interval,url,saveLoc,start):
        logging.getLogger(saveLoc).setLevel(LogLevel)
        self._timer     = None
        self.interval   = interval
        self.function   = downloadImage
        self.url        = url
        self.saveLoc    = saveLoc
        self.is_running = False
        self._timer = Timer(self.interval, self._run)
        self._timer.setName(self.saveLoc)
        self.restart(start)

    def _run(self):
        self.is_running = False
        self.start()
        self.function(self.url,self.saveLoc)
        logging.getLogger(self.saveLoc).info("Downloading new Image.")

    def start(self):
        logging.getLogger(self.saveLoc).debug("Start called!")
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.setName(self.saveLoc)
            self._timer.start()
            self.is_running = True
        
    def restart(self,start):
        self._starttimer = Timer((start-datetime.datetime.now()).seconds, self.start)
        self._starttimer.setName(self.saveLoc)
        self._starttimer.start()
    
            
    def stop(self):
        self._starttimer.cancel()
        self._timer.cancel()
        self.is_running = False
 

    
    
def main():
    global AnimateTimer
    now = datetime.datetime.now()
    start = datetime.datetime(now.year,now.month,now.day,now.hour+1)
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
        except Exception as e:
            log.error("Could not create folder "+x+"!")
            log.error("Exception: "+str(e))
        log.info("Added Camera "+x)
        cameras[x]["instance"] = RepeatingDownload(cameras[x]["wait"]*60,cameras[x]["url"],x,start)
    
    while True:
        command = input(">")
        if command == "list-cams":
            for x in cameras.keys():
                log.info(x +": Running? "+str(cameras[x]["instance"].is_running) +" Waiting? "+str(cameras[x]["instance"]._starttimer.is_alive()))
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
                log.info("Camera "+cam+" schedualed to start!")
                now = datetime.datetime.now()
                start = datetime.datetime(now.year,now.month,now.day,now.hour+1)
                cameras[cam]["instance"].restart(start)
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