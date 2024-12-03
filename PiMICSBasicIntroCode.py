import time
from picamera2 import Picamera2
from gpiozero import LED
from time import sleep
import numpy as np
import cv2
import matplotlib.pyplot as plt
from datetime import datetime

#define which GPIO pin lights up which LED

pin445=LED(2)
pin520=LED(3)
pin580=LED(4)
pin620=LED(17)
pin660=LED(27)
pin680=LED(22)
pin730=LED(10)
pin760=LED(9)
pin800=LED(11)
pin850=LED(5)
pin880=LED(6)
pin940=LED(13)

#make an array with the pins.  This is useful in simplifying the programming.
pincolor=[pin445,pin520,pin580,pin620,pin660,pin680,pin730,pin760,pin800,pin850,pin880,pin940]
colors=[445,520,580,620,660,680,730,760,800,850,880,940]

#initialize the GPIO pins to off
for color in pincolor:
    color.off()

picam2 = Picamera2() #Defining picam2
picam2.configure(picam2.create_preview_configuration()) #configuring the camera
picam2.set_controls({"ExposureTime":6000,"AnalogueGain":1.0}) #This sets the exposure time in microseconds and the gain
picam2.start()


sleepPhoto=.1 #This is the time between sequential images in seconds

sleepCamera=12*3600 #This is the time between successive measurements in seconds.


#Gives time for the camera to set
sleep(3)

NumColors=len(colors)
#This will have the normalized spectrum of pixel


AvoSpec1=np.zeros(NumColors) #This is the average spectral reflectance over the rectangular area for avocado 1
AvoSpec2=np.zeros(NumColors)  #Similar

Trials=20
HyperImage=np.zeros((480,640,NumColors)) #Create multispectral data cube each pixel has the number of colors

for m in range(0,Trials):
    i=0
    ave=np.zeros(3)
    ave=np.zeros(3) #Used to find the average value of each color
    Year= datetime.now().year     # the current year
    Month = datetime.now().month    # the current month
    Day= datetime.now().day      # the current day
    Hour= datetime.now().hour   # the current hour
    Minute= datetime.now().minute # the current minute
    for color in pincolor:
        now=datetime.now() #find the current time
        color.on() #turns on an LED
        sleep(sleepPhoto) #Waits for 
        
        frame = picam2.capture_array()  #Captures images as arrays for manipulation in Numpy
        
        framePure=frame.copy() #copy an image
        for j in range(0,3): #This is a reference region of a white piece of paper
            ave[j]=np.average(frame[270:400,250:310,j])
        AM=np.argmax(ave) #AM means argument of the maximum.  It finds the color with the largest amplitude for the reference
        HyperImage[:,:,i]=frame[:,:,AM]/ave[AM] #This is the time-evolved hypercube. This records the brightness of every pixel at each wavelength relative to the reference for every trial
        avo1=np.average(frame[270:400,40:80,AM]) #find the average value of the brightest color in the avocado
        avo2=np.average(frame[270:400,460:500,AM]) #similar
        Ratio1=round(avo1/ave[AM],3) #Take the ratio of the average against the reference.
        Ratio2=round(avo2/ave[AM],3) #similar
        AvoSpec1[i]=Ratio1 #Fills in one element in the spectrum
        AvoSpec2[i]=Ratio2 #similar
        
        print(colors[i])
        print('Color=R G B=',ave[0],ave[1],ave[2])        
        print('________________________________________________________')
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #converts Blue Green Red to Red Green Blue.  opencv uses BGR but libcamera2 uses RGB

        cv2.rectangle(frame_rgb,(40,270),(80,400),(255,255,255)) #draws a rectangle around the region where the average is performed for avocado1
        cv2.rectangle(frame_rgb,(250,270),(310,400),(255,255,255)) #similar, but for reference region
        cv2.rectangle(frame_rgb,(460,270),(500,400),(255,255,255)) #similar, but for avocado 2
        
        #These next few lines put text on the images with relevant information like, data, wavelength, ratios and
        cv2.putText(img=frame_rgb, text=str(colors[i])+' nm ', org=(30, 50), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=.4, color=(255, 255, 255),thickness=1)
        cv2.putText(img=frame_rgb, text=str(Year)+'/'+str(Month)+'/'+str(Day)+' '+str(Hour)+':'+str(Minute), org=(30, 80), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=.4, color=(255, 255, 255),thickness=1)
        cv2.putText(img=frame_rgb, text=str(Ratio1), org=(40, 420), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=.4, color=(255, 255, 255),thickness=1)
        cv2.putText(img=frame_rgb, text=str(Ratio2), org=(460, 420), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=.4, color=(255, 255, 255),thickness=1)
        cv2.imwrite('/home/shunzhang/HyperPiImages/Images2_Avocados_6_10_2024_to_6_20_2024/Avocado'+str(i)+'_'+str(Month)+'_'+str(Day)+'_'+str(Hour)+':'+str(Minute)+'.png',frame_rgb)
        
        sleep(sleepPhoto)
        color.off()
        i=i+1
    plt.figure(dpi=150,figsize=(4,3))
    plt.plot(colors,AvoSpec1,label='Avocado 1')
    plt.plot(colors,AvoSpec2,label='Avocado 2')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Reflectance')
    plt.legend(loc='upper left')
    plt.savefig('/home/shunzhang/HyperPiImages/Images2_Avocados_6_10_2024_to_6_20_2024/SpectralPlot_'+str(Month)+'_'+str(Day)+'_'+str(Hour)+':'+str(Minute)+'.png')
    if m==Trials-1:
        sleep(1)
        print('End')
    else:
        print('iteration '+str(m+1)+' out of '+str(Trials)+' trials')
        sleep(sleepCamera)
picam2.close()



# Helpful commands

#testing the capture array command of the camera and processing to opencv output against
#picamera2 capture_file command
#picam2.capture_file("/home/shunzhang/HyperPiImages/Images_1/test.jpg")
#testframe = picam2.capture_array()
#cv2.imwrite('/home/shunzhang/HyperPiImages/Images_1/test2',testframe)


