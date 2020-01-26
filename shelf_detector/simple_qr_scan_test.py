import os
from simple_qr_scan import qr_scan_image

print("Ingesting images...")

current_path = os.path.abspath(os.path.dirname(__file__))
input_path = os.path.join(current_path, "../front_images/")

output_path = os.path.join(current_path, "../web_monitor/output_front_images/")

for file in sorted(os.listdir(input_path)):
    #print((path + str(files)))
    if file.startswith('.') is False:
        image_to_scan_path = input_path + str(file)
        qr_scan_image(image_to_scan_path,output_path)
