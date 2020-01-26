import ntpath
import json
import os
from inventory import Inventory
from random import randrange


inventory = Inventory()

print("Ingesting images...")

current_path = os.path.abspath(os.path.dirname(__file__))
input_path = os.path.join(current_path, "../front_images/")

output_path = os.path.join(current_path, "../web_monitor/output_front_images/")

for file in sorted(os.listdir(input_path)):
    #print((path + str(files)))
    if file.startswith('.') is False:
        image_to_scan_path = input_path + str(file)
        inventory.ingest_image(image_to_scan_path, output_path)


# Get currently owned products
print("Listing detected products...")
products = inventory.get_products()
for product in products:
    print("Name: " + product.name())
    print("Available? " + str(product.status()))


test_temp = randrange(20)
inventory.close_inventory(test_temp)
print("Close inventory at "+str(test_temp)+" degree and print yml")


print( inventory.inventory_as_string() )
