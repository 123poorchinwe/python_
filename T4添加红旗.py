# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 23:04:06 2022

@author: Hello
"""

# resize-and-add-logo.py
# This script helps resize all images in the given directory to 
# fit in a 1920x1280 screen(especially the width), and add catlogo.png to the lower-right corner.
import os
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True # tolerate large image file

FIT_WIDTH = 700
LOG_WIDTH = 200
LOGO_FILENAME = "E:/派森/期末/T4/flag.png" # in current working directory
GIVEN_DIR ="E:\派森\期末\T4\withLogo1/"
logoIm = Image.open(LOGO_FILENAME)
logoWidth, logoHeight = (50,50) # (808,768)
logoHeight, logoWidth = (50,50)
logoIm = logoIm.resize((logoWidth, logoHeight))

os.makedirs('withLogo', exist_ok = True) # create a directory to save changed images
for filename in os.listdir(GIVEN_DIR):
    if not (filename.endswith('.png') or filename.endswith('.jpg')):
        continue # skip non-image files
    im = Image.open(os.path.join(GIVEN_DIR, filename))
    width, height = im.size
    if width > FIT_WIDTH:
        height = int((FIT_WIDTH / width) * height)
        width = FIT_WIDTH
    print('Resizing {}...'.format(filename)) 
    im = im.resize((width, height)) # resize the image
    print('Adding logo to {}...'.format(filename))
    im.paste(logoIm, (300, 50), logoIm) # add the logo
    im.save(os.path.join('withLogo', filename)) # save changes
