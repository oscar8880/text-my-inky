import sys
import time

from inky.inky_uc8159 import Inky

inky = Inky()
saturation = 0.5

def show_image(image):
    inky.set_image(image, saturation=saturation)
    inky.show()