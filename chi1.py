import urllib
import time
from PIL import Image

last = []
count = 0

def downloadImage(URL):
    global last
    global count
    url = urllib.urlopen(URL)
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
        downloadImage("https://www.glerl.noaa.gov/metdata/chi/chi1.jpg")
    except:
        pass
    if t < count:
        print "Download happened! "
    else:
        print "Image did not change!"
   
    time.sleep(120)
