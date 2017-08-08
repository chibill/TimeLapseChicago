import urllib2
import time
from PIL import Image

last = []
count = 0

def downloadImage(URL):
    global last
    global count
    url = urllib2.urlopen(URL)
    temp = Image.open(url)
    url.close()
    if not list(temp.getdata())== last:
        temp.save(str(count)+".jpg")
        last = list(temp.getdata())
        count +=1
    temp.close()

while True:
    print "Attemping downloads!"
    t=count
    try:
        downloadImage("http://cdn.abclocal.go.com/three/wls/webcam/Loopscape.jpg")
    except Exception as e:
        print e
    if t < count:
        print "Download happened! "
    else:
        print "Image did not change!"
   
    time.sleep(60)
