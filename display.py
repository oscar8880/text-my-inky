import sys
import time

from inky.inky_uc8159 import Inky

inky = Inky()
saturation = 0.5

def inky_display(image):
    # convert image to allow for PNGs
    converted_image = image.convert('RGB')
    converted_image.show()
    inky.set_image(converted_image, saturation=saturation)
    inky.show()