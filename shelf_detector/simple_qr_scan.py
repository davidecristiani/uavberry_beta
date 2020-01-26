from pyzbar.pyzbar import decode
from PIL import Image,ImageDraw
import ntpath
import json
import os
from enum import Enum
import time
import qrcode
from datetime import datetime


def qr_scan_image(image_to_scan_path, image_output_dir):
    image = Image.open(image_to_scan_path)
    image.save(image_output_dir + 'source/' + ntpath.basename(image_to_scan_path))
    decoded_data = decode(image)
    qrs = list()
    print("Found "+str(len(decoded_data))+" qrcode")
    for qrcoded in decoded_data:
        qrs.append(qrcoded.data)
        print("Data: "+str(qrcoded.data))
        draw = ImageDraw.Draw(image)
        draw.text((10,10), qrcoded.data, fill=(0,255,0,128))
        rect = qrcoded.rect
        draw.rectangle(((rect.left, rect.top), (rect.left + rect.width, rect.top + rect.height)), outline='#0000FF')
        draw.polygon(qrcoded.polygon, outline='#00FF00')
        image.save(image_output_dir + 'final/' + ntpath.basename(image_to_scan_path))
    return qrs
