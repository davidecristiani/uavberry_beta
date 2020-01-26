import os
from ground_inspector.ground_coordinates import ground_coordinates

def ground_vision():
    current_path = os.path.abspath(os.path.dirname(__file__))
    input_ground_image_path = os.path.join(current_path, '../ground_images/ground_image.jpg')
    output_ground_image_path = os.path.join(current_path, '../web_monitor/output_ground_images/')
    return ground_coordinates(input_ground_image_path,output_ground_image_path)
