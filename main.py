import pygame
import sys
import os
from pygame.locals import *
import pygame.camera
import time
import shutil
from skimage.measure import compare_ssim
import argparse
import imutils
import cv2



# -------------------------
# TODO: declare grayA
# --------------------------

folderName = ''
picName = 'pic.jpg'

saveAtOriPoint = 10
isStart = False
oriCount = 0
captureCount = 0

saveFloderName = 'capture'
width = 640
height = 480
t = 0


# --------------------
#         init
# --------------------

pygame.init()
pygame.camera.init()
cam = pygame.camera.Camera("/dev/video0", (width, height))
cam.start()

# setup window
windowSurfaceObj = pygame.display.set_mode((width, height), 1, 16)
pygame.display.set_caption('Camera')


def first_use():

    s = time.ctime()
    global folderName
    folderName = s[4:10]

    if not os.path.exists(folderName):
        os.makedirs(folderName)


def take_photo():

    global saveFloderName
    # cam.start()
    # take a picture
    image = cam.get_image()
    # cam.stop()
    # display the picture
    catSurfaceObj = image
    windowSurfaceObj.blit(catSurfaceObj, (0, 0))
    pygame.display.update()

    save_pic()


def save_pic():

    global t, oriCount, saveAtOriPoint, isStart

    if t >= saveAtOriPoint and not isStart:
        pygame.image.save(windowSurfaceObj, 'origin' + str(oriCount) + '.jpg')
        oriCount += 1
        if oriCount % 2 == 0:
            oriCount = 0
            cmp_pic(0)

    elif t >= saveAtOriPoint and isStart:
        pygame.image.save(windowSurfaceObj, picName)
        cmp_pic(1)


# ----------------------------------------------------------
#  mode:
#       0 ->   compare origin0  &  origin1      pic
#       1 ->   compare origin   &  this frame   pic
#
# ----------------------------------------------------------

def cmp_pic(mode):

    if mode == 0:
        imageA = cv2.imread('origin0.jpg')
        imageB = cv2.imread('origin1.jpg')
        grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
        

    else:
        global grayA
        imageB = cv2.imread(picName)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # compute the Structural Similarity Index (SSIM) between the two
    # images, ensuring that the difference image is returned
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype("uint8")

    if score > 0.925:
        if mode == 0:
            os.rename('origin0.jpg', 'origin.jpg')
            os.remove('origin1.jpg')
            global isStart
            isStart = True
            print('origin save over~')
        return
    
    
    print(time.ctime())
    print(score)

    # threshold the difference image, followed by finding contours to
    # obtain the regions of the two input images that differ
    thresh = cv2.threshold(diff, 100, 255,
                           cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # loop over the contours
    for c in cnts:
        # compute the bounding box of the contour and then draw the
        # bounding box on both input images to represent where the two
        # images differ
        (x, y, w, h) = cv2.boundingRect(c)
        if (w + h) > 150:
            cv2.rectangle(imageB, (x, y), (x + w, y + h), (0, 0, 255), 2)
    


    # display the picture
    cv2.imwrite(picName, imageB)
    catSurfaceObj = pygame.image.load(picName)
    windowSurfaceObj.blit(catSurfaceObj, (0, 0))
    pygame.display.update()
    
    s = time.ctime()
    f = s[11:19] + '.jpg'
    os.rename(picName, f)
    shutil.move(f, folderName + '/' + f)
    print('warning')
    


first_use()


while True:

    take_photo()

    t += 1
    time.sleep(1)
    #cam.stop()


