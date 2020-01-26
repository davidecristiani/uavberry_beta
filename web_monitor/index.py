#!/usr/bin/env python
from flask import (Flask, flash, redirect, render_template, request, send_file, send_from_directory, session, url_for, Blueprint)
import os
import yaml


app = Flask(__name__)
app.secret_key = '_5d4d8z.!/'

@app.errorhandler(404)
def page_not_found(e):
    return send_from_directory('layout_images', '404.png'), 404

@app.route('/output_ground_images/<path:path>')
def send_ground_images(path):
    return send_from_directory('output_ground_images', path)

@app.route('/output_front_images/<path:path>')
def send_front_images(path):
    return send_from_directory('output_front_images', path)

@app.route('/')
def index():

    web_monitor_current_path = os.path.abspath(os.path.dirname(__file__))
    output_front_image_final = 'not_found.png'
    output_front_images_final_path = os.path.join(web_monitor_current_path, "../web_monitor/output_front_images/final/")
    for file in sorted(os.listdir(output_front_images_final_path)):
        if file.startswith('.') is False:
            output_front_image_final = str(file)
    output_ground_image_final = 'not_found.png'
    output_ground_images_final_path = os.path.join(web_monitor_current_path, "../web_monitor/output_ground_images/final/")
    for file in sorted(os.listdir(output_ground_images_final_path)):
        if file.startswith('.') is False:
            output_ground_image_final = str(file)

    return render_template('index.html', last_ground_image=output_ground_image_final, last_front_image=output_front_image_final)

@app.route('/ground')
def ground():

    web_monitor_current_path = os.path.abspath(os.path.dirname(__file__))

    output_ground_images_source_path = os.path.join(web_monitor_current_path, "../web_monitor/output_ground_images/source/")
    all_ground_image_source = list()
    for file in sorted(os.listdir(output_ground_images_source_path)):
        if file.startswith('.') is False:
            all_ground_image_source.insert(0,str(file))

    return render_template('ground.html', all_ground_image_source=all_ground_image_source)

@app.route('/front')
def front():

    web_monitor_current_path = os.path.abspath(os.path.dirname(__file__))

    output_front_images_source_path = os.path.join(web_monitor_current_path, "../web_monitor/output_front_images/source/")
    all_front_image_source = list()
    for file in sorted(os.listdir(output_front_images_source_path)):
        if file.startswith('.') is False:
            all_front_image_source.insert(0,str(file))

    return render_template('front.html', all_front_image_source=all_front_image_source)


@app.route('/inventories')
def inventories():
    web_monitor_current_path = os.path.abspath(os.path.dirname(__file__))
    output_inventories_path = os.path.join(web_monitor_current_path, "../web_monitor/inventories/")
    inventories = list()
    for file in sorted(os.listdir(output_inventories_path)):
        if file.endswith('.yaml') is True:
            output_inventory_file_path = os.path.join(output_inventories_path, file)
            with open(output_inventory_file_path, 'r') as stream:
                try:
                    yaml_content = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    return(exc)
            yaml_content['file'] = file
            if os.path.isfile((output_inventories_path+file+".ots")):
                yaml_content['ots'] = 'true'
            inventories.insert(0,yaml_content)
    return render_template('inventories.html', inventories=inventories)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
