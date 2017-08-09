import timelapse
import Timer


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
