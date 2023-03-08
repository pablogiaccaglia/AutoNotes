import os

import cv2
import pytesseract
import matplotlib.pyplot as plt
import numpy as np


def img2text(image):

    # convert the image to black and white for better OCR
    ret, thresh1 = cv2.threshold(image, 120, 255, cv2.THRESH_BINARY)
    #thresh1 = 255-thresh1
    """plt.imshow(thresh1)
    plt.show()"""

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

"""image = cv2.imread("Page_2.jpg")
print(img2text(image))"""
"""# get co-ordinates to crop the image
im, line_items_coordinates = mark_region(image_path = 'Page_2.jpg', relaxation =0)
plt.imshow(im)
plt.show()
"""

"""lines_clean = clean_rois(line_items_coordinates, threshold = 30)


for l in lines_clean:
    x,y,z,q = l[0][0], l[0][1], l[1][0], l[1][1]
    image = cv2.rectangle(image, (x, y), (z,q), color = (255, 0, 255), thickness = 3)


plt.imshow(image)
plt.show()
# cropping image img = image[y0:y1, x0:x1]


for c in lines_clean:
    img = image[c[0][1]:c[1][1], c[0][0]:c[1][0]]

    plt.figure(figsize=(10,10))
    plt.imshow(img)
    plt.show()

    # convert the image to black and white for better OCR
    ret,thresh1 = cv2.threshold(img,120,255,cv2.THRESH_BINARY)

    # pytesseract image to string to get results
    text = str(pytesseract.image_to_string(thresh1, config='--psm 6'))
    print(text)
"""