#!/usr/bin/python

import sys
import ftplib
import os
import time
from shutil import copyfile

def ftp_download():
    
    server = "192.168.99.3"
    user = "anonymous"
    password = "anonymous"
    path = "/internal_000/Mambo/media/"
    path_thumb = "/internal_000/Mambo/thumb/"
    current_path = os.path.abspath(os.path.dirname(__file__))
    destination = os.path.join(current_path, '../ground_images/')

    destination_file = os.path.join(destination, 'ground_image_'+str(time.time())+'.jpg')
    destination_file_now = os.path.join(destination, 'ground_image.jpg')
    os.chdir(destination)
	
    ftp = ftplib.FTP(server)
    ftp.login(user, password)
    
    ftp.cwd(path)       
    filelist=ftp.nlst()
    for file in filelist:
        try:
            ftp.retrbinary("RETR " + file, open(destination_file,"wb").write)
            ftp.delete(file)
            copyfile(destination_file, destination_file_now)
            print("Downloaded: " + file)
        except:
            print("Error: File could not be downloaded " + file)
    ftp.cwd(path_thumb)       
    filelist=ftp.nlst()
    for file in filelist:
        try:
            ftp.delete(file)
            #print("Delete: " + file)
        except:
            print("Error: File could not be delete " + file)
    return destination_file
    