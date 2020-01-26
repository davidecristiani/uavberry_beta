# COMMAND 15 BACK AND FRONT CAMERA SIMPLEQR - FLIGHT
from pyparrot.Minidrone import Mambo
from ground_inspector.ftp_download import ftp_download
from ground_inspector.ground_vision import ground_vision
from shelf_detector.simple_qr_scan import qr_scan_image
from pyparrot.DroneVision import DroneVision
import threading
import cv2
import time
import os

class UserVision:
    def __init__(self, vision):
        self.index = 0
        self.vision = vision

    def save_pictures(self, args):

        img = self.vision.get_latest_valid_picture()

        if (img is not None):

            command_front_input_path = '/home/pi/Desktop/front_images/'
            command_front_output_path = '/home/pi/Desktop/web_monitor/output_front_images/'

            command_front_filename = command_front_input_path+'front_image_'+str(time.time())+".png"
            command_front_filename_static = command_front_input_path+"front_image.png"

            print(command_front_filename )
            cv2.imwrite(command_front_filename, img)
            cv2.imwrite(command_front_filename_static, img)
            qr_scan_image(command_front_filename_static,command_front_output_path)
            qr_scan_image(command_front_filename,command_front_output_path)
            self.index +=1
            print(self.index )

mamboAddr = "e0:14:d0:63:3d:d0"
os.path.join(os.path.dirname(__file__))
mambo = Mambo(mamboAddr, use_wifi=True)

print("trying to connect")
success = mambo.connect(num_retries=3)
print("connected: %s" % success)

if (success):
    print("sleeping")
    mambo.smart_sleep(1)
    mambo.ask_for_state_update()
    mambo.smart_sleep(2)

    print("Preparing to open vision")
    mamboVision = DroneVision(mambo, is_bebop=False, buffer_size=30)
    userVision = UserVision(mamboVision)
    mamboVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
    success = mamboVision.open_video()
    print("Success in opening vision is %s" % success)
    mambo.smart_sleep(2)
    mambo.safe_takeoff(5)


    if (mambo.sensors.flying_state != "emergency"):



        for i in range(200):

            mambo.smart_sleep(2)
            pic_success = mambo.take_picture()
            mambo.smart_sleep(1)
            ftp_download()
            ground_coordinates_value = ground_vision()
            if ground_coordinates_value is None:
                # There are not houghes circles in the pic. No hay problema, I will cotinue on my way
                pass
            else:
                (angle_r_s, x_vector_g_m, y_vector_g_m) = ground_coordinates_value
                print("Drone Rotate of degree "+str(angle_r_s))
                if angle_r_s > 180:
                    mambo.turn_degrees(angle_r_s-360)
                else:
                    mambo.turn_degrees(angle_r_s)

            # uav looks left
            mambo.smart_sleep(2)
            mambo.turn_degrees(-90)

            # uav looks straight
            mambo.smart_sleep(1)
            mambo.turn_degrees(90)

            # uav looks right
            mambo.smart_sleep(1)
            mambo.turn_degrees(90)

            # uav looks straight
            mambo.smart_sleep(1)
            mambo.turn_degrees(-90)

            mambo.smart_sleep(2)
            mambo.fly_direct(roll=0, pitch=3, yaw=0, vertical_movement=0)

        mambo.safe_land(5)
        mambo.smart_sleep(2)

    print("Ending the sleep and vision")
    mamboVision.close_video()

    mambo.smart_sleep(2)

    print("disconnect")
    mambo.disconnect()
