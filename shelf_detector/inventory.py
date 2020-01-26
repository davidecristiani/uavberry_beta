from pyzbar.pyzbar import decode
from PIL import Image,ImageDraw
import ntpath
import os
import enum
import time
import qrcode
from datetime import datetime
import yaml

current_path = os.path.abspath(os.path.dirname(__file__))

#   Folder were we put YAML models to be converted
JSON_MODELS_FOLDER = os.path.join(current_path, "product_models")
#   Folder were we put YAML -> QRCode images
QR_CODES_FOLDER = os.path.join(current_path, "images_inventory")
#   Folder were to store inventory.json storage support
INVENTORY_DB_PATH = os.path.join(current_path, "inventories")
#   Folder where to store backup copies of inventory.yaml
INVENTORY_DB_BACKUP_PATH = os.path.join(current_path, "../web_monitor/inventories")

"""

#   Product data model

i: 1
n: chesee
s: 1
m: 20
g: 25

"""



class Availability(enum.IntEnum):
    AVAILABLE = 1,
    SCHEDULED = 2,
    NOT_AVAILABLE = 3



class Product:

    def __init__(self, json):
        self.i = json['i']
        self.n = json['n']
        self.s = json['s']
        self.m = json['m']
        self.g = json['g']

    def id(self):
        return self.i

    def name(self):
        return self.n

    def status(self):
        if(self.s == 1):
            return Availability.AVAILABLE
        elif(self.s == 2):
            return Availability.SCHEDULED
        else:
            return Availability.NOT_AVAILABLE

    def min_temperature(self):
        return self.m

    def max_temperature(self):
        return self.g



class Inventory:

    db_name = os.path.join(INVENTORY_DB_PATH, "inventory.yaml")
    backup_db_name = os.path.join(INVENTORY_DB_BACKUP_PATH, "inventory.yaml")

    def __init__(self):
        if not os.path.exists(INVENTORY_DB_PATH):
            os.makedirs(INVENTORY_DB_PATH)
        if not os.path.exists(INVENTORY_DB_BACKUP_PATH):
            os.makedirs(INVENTORY_DB_BACKUP_PATH)
        if not os.path.exists(QR_CODES_FOLDER):
            os.makedirs(QR_CODES_FOLDER)
        self.db_name = os.path.join(INVENTORY_DB_PATH, "inventory-" + str(datetime.now()).replace(":", "-") + ".yaml")
        self.backup_db_name = os.path.join(INVENTORY_DB_BACKUP_PATH, "inventory-" + str(datetime.now()).replace(":", "-") + ".yaml")
        if not os.path.exists(self.db_name):
            data = { 'products' : [ ] }
            with open(self.db_name, "w+") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    #
    #   Populate inventory with test data, simulates a drone scanning
    #
    def populate_inventory_from_yaml_models(self):
        for files in sorted(os.listdir(JSON_MODELS_FOLDER)):
            with open(os.path.join(JSON_MODELS_FOLDER, str(files))) as f:
                self.ingest_yaml(yaml.safe_load(f))

    #
    #   Ingest a new json to add to the inventory (also creates its QR code)
    #
    def ingest_yaml(self, ya):
        product = Product(ya)
        label = product.name() + "-" + str(product.status())
        image_path = os.path.join(QR_CODES_FOLDER, label + '.png')
        i = 1
        while os.path.exists(image_path):
            image_path = os.path.join(QR_CODES_FOLDER, label + '-' + str(i) + '.png')
            i = i + 1
        qr = qrcode.QRCode(
            version = None,
            error_correction = qrcode.constants.ERROR_CORRECT_L,
            box_size = 10,
            border = 8,
        )
        qr.add_data(ya)
        qr.make(fit = True)
        qr.make_image(fill_color = "black", back_color = "white").save(image_path)
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        width, height = image.size
        w, h = draw.textsize(label)
        draw.text(((width - w) / 2, (height - height + h * 2)), label, fill = "black")
        image.save(image_path)
        self.ingest_image(image_path, None)

    #
    #   Ingest a new image to scan inventory population
    #
    def ingest_image(self, image_path, image_output_dir):
        products = self.product_detection(image_path, image_output_dir)
        for product in products:
            if not self.__is_in_inventory(product):
                self.__add_to_inventory(product)
            elif not self.__is_product_updated(product):
                self.__update_product(product)

    #
    #
    #
    def get_products(self):
        products = list()
        with open(self.db_name) as f:
            data = yaml.safe_load(f)

            for p in data['products']:
                products.append(Product(p))
        return products

    #
    #   Close inventory and backup it
    #
    def close_inventory(self, temperature):
        with open(self.db_name) as f:
            data = yaml.safe_load(f)
            data['temperature'] = temperature
            data['time'] = str(datetime.now())

        with open(self.db_name, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)

        with open(self.backup_db_name, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)

    #
    #   Get inventory file as string
    #
    def inventory_as_string(self):
        data = ""
        with open(self.db_name) as f:
            data = f.readlines()
        return data

    #
    #   Send restock requests to all items that are missing in the inventory
    #
    def send_stock_requests(self):
        with open(self.db_name) as f:
            data = yaml.safe_load(f)

            for p in data['products']:
                if p['s'] == 3:
                    # HTTP to p['supplier']['endpoint']
                    p['s'] = 2

        with open(self.db_name, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)

    #
    #   Clean supply request when new supplies for a given product arriva to the inventory
    #
    def stock_arrived(self):
        with open(self.db_name) as f:
            data = yaml.safe_load(f)

            for p in data['products']:
                if p['s'] == 2:
                    p['s'] = 1

        with open(self.db_name, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)

    #
    #   Check if a product is already in the inventory
    #
    def __is_in_inventory(self, product):
        with open(self.db_name) as f:
            data = yaml.safe_load(f)
            for p in data['products']:
                if p['i'] == product.id():
                    return True
        return False

    #
    #   Check if supply alert was already noticed for a gived product
    #
    def __is_product_updated(self, product):
        with open(self.db_name) as f:
            data = yaml.safe_load(f)
            for p in data['products']:
                if p['i'] == product.id():
                    if p['s'] == product.status() == Availability.AVAILABLE:
                        return True
                    elif p['s'] == product.status() == Availability.NOT_AVAILABLE:
                        return True
                    elif p['s'] == 2 and product.status() == Availability.NOT_AVAILABLE:
                        return True
        return False

    #
    #   Add a new product to the inventory
    #
    def __add_to_inventory(self, product):
        with open(self.db_name) as f:
            data = yaml.safe_load(f)

            data['products'].append(product.__dict__)

            print(data)

        with open(self.db_name, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)

    #
    #   Add supply alert for a given product
    #
    def __update_product(self, product):
        with open(self.db_name) as f:
            data = yaml.safe_load(f)

            for p in data['products']:
                if p['i'] == product.id():
                    p['s'] = int(product.status())

        with open(self.db_name, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)

    #
    #   Get the list of available Product models in the image
    #
    def product_detection(self, image_path, image_output_dir):
        qr_codes = self.qr_codes_detection(image_path, image_output_dir)
        products = list()
        if(qr_codes is None):
            return products
        for qrc in qr_codes:
            try:
                qr_json = yaml.safe_load(qrc)
                products.append(Product(qr_json))
            except yaml.YAMLError as e:
                print(str(e))
                None
        return products

    #
    #   Get the list of QRcade data available in the image to be processed
    #
    def qr_codes_detection(self, image_to_scan_path, image_output_dir):
        image = Image.open(image_to_scan_path)
        if (image_output_dir):
            image.save(os.path.join(image_output_dir, 'source', ntpath.basename(image_to_scan_path)))
        decoded_data = decode(image)
        qrs = list()
        print('Number of found QRCodes: '+str(len(decoded_data)))
        for qrcoded in decoded_data:
            qrs.append(qrcoded.data)
            print('QRCode data: '+str(qrcoded.data))
            if (image_output_dir):
                draw = ImageDraw.Draw(image)
                draw.text((10,10), qrcoded.data, fill=(0,255,0,128))
                rect = qrcoded.rect
                draw.rectangle(((rect.left, rect.top), (rect.left + rect.width, rect.top + rect.height)), outline='#0000FF')
                draw.polygon(qrcoded.polygon, outline='#00FF00')
                image.save(os.path.join(image_output_dir, 'final', ntpath.basename(image_to_scan_path)))
        return qrs

    #
    #   Debug function to get QRCodes pixel area
    #
    def PolygonArea(self, corners):
        n = len(corners) # of corners
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += corners[i][0] * corners[j][1]
            area -= corners[j][0] * corners[i][1]
        area = abs(area) / 2.0
        return area
