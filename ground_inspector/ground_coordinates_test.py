import os
from ground_coordinates import ground_coordinates

print("Ground coordinates images...")

current_path = os.path.abspath(os.path.dirname(__file__))
input_path = os.path.join(current_path, "../ground_images/")
output_path = os.path.join(current_path, "../web_monitor/output_ground_images/")

for file in sorted(os.listdir(input_path)):
    if file.startswith('.') is False:
        image_to_scan_path = input_path + str(file)
        ground_coordinates(image_to_scan_path,output_path)
