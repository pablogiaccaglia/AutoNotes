import os

import cv2
import pytesseract
import matplotlib.pyplot as plt
import numpy as np


def img2text(image):

    # convert the image to black and white for better OCR
    ret, thresh1 = cv2.threshold(image, 120, 255, cv2.THRESH_BINARY)

    # pytesseract image to string to get results
    text = pytesseract.image_to_string(thresh1, config = '--psm 4 --oem 1', lang='eng')

    if not text:
        text = pytesseract.image_to_string(thresh1, config = '--psm 6 --oem 1', lang='eng')
        return text

    else:
        text = os.linesep.join([s for s in text.splitlines() if s])
        l = text.splitlines()
        if len(l) > 1:
            l = l[:-1]
        new_lines = []
        for line in l:
            if line[0] in ['®', '#', '=', '"', '»', '°', '¢']:
                line = "- " + " ".join(line.split(" ")[1:])

            new_lines.append(line)

        text = os.linesep.join(new_lines)
        return text