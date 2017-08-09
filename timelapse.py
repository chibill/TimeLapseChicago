from six.moves.urllib import request
from six.moves import input
from threading import Timer
from threading import enumerate as Threads
import time
import json
from glob import glob
import os
import datetime
import imageio
import logging

LogLevel = 20

AnimateTimer = None

def downloadImage(URL,saveLoc):
    url = request.urlopen(URL)
    file = open(saveLoc+"/"+str(int(time.time()))+".jpg","wb+")
    file.write(url.read())
    file.flush()
    file.close()
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
 
def animate(cams):
    global AnimateTimer
    for x in cams.keys():
        with imageio.get_writer(x+'.mp4', mode='I',fps=cams[x]["fps"],ffmpeg_log_level="quiet") as writer:
            for y in glob(x+"/"+"*.jpg"):
                try:
                    image = imageio.imread(y)
                    writer.append_data(y)
                except Exception as e:
                    log = logging.getLogger("Animate")
                    log.setLevel(LogLevel)
                    log.error("Could not read Image"+x+"/"+y+"!")
                    log.error("Exception: "+str(e))
    AnimateTimer = Timer(60*60,animate,args=[cams])
    AnimateTimer.setName("Animate")
    AnimateTimer.start()
    
    
    
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
    animate(cameras)
    
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
            AnimateTimer.cancel()
            break
        elif command == "help": 
            log.info("help: Shows this.")
            log.info("list-cams: Lists the current cameras.")
            log.info("stopcam: Stops a cameras recording.")
            log.info("startcam: Starts a camera recording.")
            log.info("stop: Stops this program.")
        elif command == "list-threads":
            log.info("Active Threads")
            for x in Threads():
                log.info(x.getName())
        else:
            log.error("Command not found! " +command)
            
            
if __name__ == "__main__":
    main()