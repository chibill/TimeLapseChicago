import imageio
import time



while True:
    with imageio.get_writer('loopscape.mp4', mode='I',fps=5) as writer:
        for filename in xrange(100000):
            try:
                image = imageio.imread('loopscape/'+str(filename)+".jpg")
                writer.append_data(image)
            except:
                break
    with imageio.get_writer('chi1.mp4', mode='I',fps=4) as writer:
        for filename in xrange(100000):
            try:
                image = imageio.imread('chi1/'+str(filename)+".jpg")
                writer.append_data(image)
            except:
                break
    with imageio.get_writer('chi2.mp4', mode='I',fps=4) as writer:
        for filename in xrange(100000):
            try:
                image = imageio.imread('chi2/'+str(filename)+".jpg")
                writer.append_data(image)
            except:
                break
    print "sleeping"
    time.sleep(60*60)
    
