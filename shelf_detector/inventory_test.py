import ntpath
import json
import os
from inventory import Inventory

current_path = os.path.abspath(os.path.dirname(__file__))
QR_CODES_FOLDER = os.path.join(current_path, "images_inventory")

inventory = Inventory()
# inventory = Inventory(True) to discard current inventory.json file

# Populate inventory using JSON data models stored in a folder, also creates their QRcode tags
print("Populating inventory with models...")
inventory.populate_inventory_from_yaml_models()

# Populate inventory using QRcode tags
print("Ingesting images...")
for files in sorted(os.listdir(QR_CODES_FOLDER)):
    if files.startswith('.') is False:
        inventory.ingest_image(QR_CODES_FOLDER + '/' + str(files), None)

# Get currently owned products
print("Listing detected products...")
products = inventory.get_products()
for product in products:
    print("Name: " + product.name())
    print("Available? " + str(product.status()))

# Send restock requests for missing products
print("Sending re-stock requests...")
inventory.send_stock_requests()

# Get currently owned products
print("Listing detected products with updated status...")
products = inventory.get_products()
for product in products:
    print("Name: " + product.name())
    print("Available? " + str(product.status()))

# Trigger restock requests cleaning when new product stocks arrive to the warehouse
print("New product stocks arrived to the warehouse...")
inventory.stock_arrived()

# Get currently owned products
print("Listing detected products with updated status...")
products = inventory.get_products()
for product in products:
    print("Name: " + product.name())
    print("Available? " + str(product.status()))

test_temp = 15
inventory.close_inventory(test_temp)
