## UAVBERRY BETA

UAVBERRY will let you control a Parrot Mambo Drone with Raspberry PI 3 B.

Front Camera pictures are processed to scan QRCodes.

This project is still *beta* stage.

Command to create the docker test environment:
* docker-compose up --build

Commands to activate the drone from Raspberry PI:

* cd /home/pi/Desktop/web_monitor/; sudo python3 index.py

* cd /home/pi/Desktop/ ; rm -f pyparrot/images/*; sudo sh delete_output_images.sh ; sudo sh delete_input_images.sh ; sudo sh connect_mambo.sh ; python3 command_14.py

* cd /home/pi/Desktop/ ; rm -f pyparrot/images/* ; sudo sh delete_output_images.sh ; sudo sh delete_input_images.sh ; sudo sh connect_mambo.sh ; python3 command_15.py
* cd /home/pi/Desktop/ ; rm -f pyparrot/images/*; sudo sh delete_output_images.sh ; sudo sh delete_input_images.sh ; sudo sh connect_mambo.sh ; python3 command_16.py

You have to manually install the **PyParrot library**.
