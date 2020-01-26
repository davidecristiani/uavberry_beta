from math import sqrt
from time import sleep
from time import time
import itertools
import math
import collections
import cv2
import ntpath
import os
import numpy as np
from random import randint
from math import sin, cos, radians

def rotate_point(point, angle, center_point=(0, 0)):
    """Rotates a point around center_point(origin by default)
    Angle is in degrees.
    Rotation is counter-clockwise
    """
    angle_rad = radians(angle % 360)
    # Shift the point so that center_point becomes the origin
    new_point = (point[0] - center_point[0], point[1] - center_point[1])
    new_point = (new_point[0] * cos(angle_rad) - new_point[1] * sin(angle_rad),
                 new_point[0] * sin(angle_rad) + new_point[1] * cos(angle_rad))
    # Reverse the shifting we have done
    new_point = (new_point[0] + center_point[0], new_point[1] + center_point[1])
    return new_point

def rotate_polygon(polygon, angle, center_point=(0, 0)):
    """Rotates the given polygon which consists of corners represented as (x,y)
    around center_point (origin by default)
    Rotation is counter-clockwise
    Angle is in degrees
    """
    rotated_polygon = []
    for corner in polygon:
        rotated_corner = rotate_point(corner, angle, center_point)
        rotated_polygon.append(rotated_corner)
    return rotated_polygon

def distance_between_dots(first_dot,second_dot):
    a_value = (abs(first_dot[0]-second_dot[0]))**2
    b_value = (abs(first_dot[1]-second_dot[1]))**2
    #print('a_value'+str(a_value))
    #print('b_value'+str(a_value))
    a_b_sum = float(a_value+b_value)
    if a_b_sum > 0:
        #print('a_b_sum: '+str(a_b_sum))
        distance_first_second_dots = round( sqrt(a_b_sum),2)
        #print('distance: '+str(distance_first_second_dots))
        return distance_first_second_dots
    else:
        return 0

def ground_coordinates(image_to_scan_path,image_output_dir):
    print('Start ground coordinates on image '+image_to_scan_path)
    #trova i cerchi e metti dei punti rossi nei centri dei cerchi
    image=cv2.imread(image_to_scan_path,0)
    original=cv2.imread(image_to_scan_path)
    cv2.imwrite(image_output_dir + 'source/' + ntpath.basename(image_to_scan_path), original)

    original_with_circles=cv2.imread(image_to_scan_path)
    #print(original)
    if original is None:
    	print('No image founded')
    	return None

    original_height, original_width, original_channels = original.shape
    ret,thresh=cv2.threshold(image,200,255,0)
    edges=cv2.Canny(image,120,250)
    cimg = cv2.cvtColor(edges,cv2.COLOR_GRAY2BGR)
    cv2.imwrite(image_output_dir + 'black/' + ntpath.basename(image_to_scan_path),cimg)

    imported_cimg=cv2.imread(image_to_scan_path,0)
    circles = cv2.HoughCircles(imported_cimg,cv2.HOUGH_GRADIENT,1,10,param1=220,param2=15,minRadius=5,maxRadius=20)

    if circles is None:
    	print('No circles founded')
    	return None

    circles = np.uint16(np.around(circles))

    # controlla che ogni punto sia allineato almeno con altri due, se non è allineato scartalo
    # trova la linea più lunga
    # traccia la perpendicolare e trova l'orientamento

    green_circles = []
    for i in circles[0,:]:
        # draw the outer circle
        if(i[2]>=0):
            circle_size = i[2]
            cv2.circle(original_with_circles,(i[0],i[1]),circle_size,(0,255,0),1)
            green_circle_coordinates_tupla = ( int(i[0]),int(i[1]) )
            green_circles.append(green_circle_coordinates_tupla)

    cv2.imwrite(image_output_dir + 'mask/' + ntpath.basename(image_to_scan_path),original_with_circles)

    green_cluster_matrix = list(itertools.combinations(green_circles, 9))
    print(str(len(green_circles))+' - cluster '+str(len(green_cluster_matrix)))

    at_least_one_image_is_similar = False
    labels_top_margin = 0
    for red_dots in green_cluster_matrix:

        max_distance_first_second_dots = 0
        longest_segment = None
        #print(time()+len(red_dots))

        for first_dot in red_dots:
            for second_dot in red_dots:
                distance_first_second_dots = distance_between_dots(first_dot,second_dot)
                if distance_first_second_dots > max_distance_first_second_dots:
                    max_distance_first_second_dots = distance_first_second_dots
                    a_dot = first_dot
                    b_dot = second_dot

        # print(" Point 2 ")

        max_distance_a_i_dots = 0
        c_dot = None
        for i_dot in red_dots:
            distance_a_i_dots = distance_between_dots(a_dot,i_dot)
            distance_b_i_dots = distance_between_dots(b_dot,i_dot)
            if distance_a_i_dots > max_distance_a_i_dots:
                if i_dot != b_dot:
                    max_distance_a_i_dots = distance_a_i_dots
                    c_dot = i_dot

        #print(b_dot)
        #print(c_dot)

        d_dot = (int((a_dot[0]+b_dot[0])/2),int((a_dot[1]+b_dot[1])/2))

        v_x = d_dot[0] - b_dot[0]
        v_y = d_dot[1] - b_dot[1]
        mag = sqrt (v_x*v_x + v_y*v_y)
        v_x = v_x / mag
        v_y = v_y / mag
        temp = v_x
        v_x = -v_y
        v_y = temp

        e_f_line_half_length = max_distance_a_i_dots/5
        e_dot = (int(d_dot[0] + v_x * e_f_line_half_length), int(d_dot[1] + v_y * e_f_line_half_length))
        f_dot = (int(d_dot[0] + v_x * -e_f_line_half_length), int(d_dot[1] + v_y * -e_f_line_half_length))

        if(distance_between_dots(e_dot,c_dot)>distance_between_dots(f_dot,c_dot)):
            g_dot = e_dot
        else:
            g_dot = f_dot



        h_dot = ( int(0), int(original_height/2) )
        i_dot = ( int(original_width), int(original_height/2) )
        m_dot = ( int(original_width/2), int(original_height/2) )



        # se d_y minore di g_y , allora d è più in alto rispetto a g
        # quindi il triangolo è voltato verso l'alto
        # di conseguenza chi fra il minore fra a_x e b_x è r_x

        # se d_y maggiore di g_y , allora d è più in alto rispetto a g
        # quindi il triangolo è voltato verso l'alto
        # di conseguenza chi fra il minore fra a_x e b_x è s_x

        if d_dot[1] <= g_dot[1]:
            if a_dot[0] <= b_dot[0]:
                r_dot = a_dot
                s_dot = b_dot
            else:
                s_dot = a_dot
                r_dot = b_dot
        else:
            if a_dot[0] <= b_dot[0]:
                s_dot = a_dot
                r_dot = b_dot
            else:
                r_dot = a_dot
                s_dot = b_dot


        rad_r_s = np.arctan2(r_dot[1] - s_dot[1], r_dot[0] - s_dot[0])

        angle_r_s = round(np.rad2deg(rad_r_s))

        if(angle_r_s>360):
            angle_r_s= angle_r_s-180
        else:
            angle_r_s = angle_r_s+180


        rotated_points = rotate_polygon(red_dots,(-angle_r_s),d_dot)


        x_array = list()
        y_array = list()
        for rotated_point in rotated_points:
            x_array.append(int(rotated_point[0]))
            y_array.append(int(rotated_point[1]))

        leftiest = min(x_array)
        rightest = max(x_array)
        lowest = min(y_array)
        highest = max(y_array)

        new_points = list()
        for rotated_point in rotated_points:
            new_point_x = rotated_point[0]-leftiest
            new_point_y = rotated_point[1]-lowest
            new_points.append((new_point_x,new_point_y))


        proportion = 5/max_distance_first_second_dots

        resized_points = list()
        for new_point in new_points:
            resized_point_x = int(new_point[0]*proportion)
            resized_point_y = int(new_point[1]*proportion)
            resized_points.append((resized_point_x,resized_point_y))

        resized_points.sort()
        #print(resized_points)
        confrontation = [(0, 2), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2), (3, 1), (3, 2), (5, 2)]
        #cv2.imwrite(image_to_scan_path+"_resizedblank"+extension,resizedblankimage)
        image_are_similar = False

        if resized_points == confrontation:
            at_least_one_image_is_similar = True

            cv2.circle(original,(c_dot[0],c_dot[1]),2,(0,255,0),2)
            cv2.circle(original,(d_dot[0],d_dot[1]),2,(0,255,0),2)
            cv2.circle(original,(e_dot[0],e_dot[1]),2,(0,255,0),2)
            cv2.circle(original,(f_dot[0],f_dot[1]),2,(0,255,0),2)
            cv2.circle(original,(g_dot[0],g_dot[1]),1,(0,255,0),1)
            cv2.circle(original,(g_dot[0],g_dot[1]),8,(0,255,0),1)
            cv2.line(original,a_dot,b_dot,(0,255,0),1)
            cv2.circle(original,(h_dot[0],h_dot[1]),2,(255,0,0),2)
            cv2.circle(original,(i_dot[0],i_dot[1]),2,(255,0,0),2)
            cv2.circle(original,(m_dot[0],m_dot[1]),2,(255,0,0),2)
            cv2.line(original,h_dot,i_dot,(255,0,0),1)
            cv2.putText(original, 'R', r_dot, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
            cv2.putText(original, 'S', s_dot, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
            cv2.putText(original, 'G', g_dot, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
            cv2.putText(original, 'D', d_dot, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
            cv2.putText(original, 'M', m_dot, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0))

            label = "Rotation in degrees "+str(angle_r_s)
            cv2.putText(original, label, (0, 15+labels_top_margin), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))

            x_vector_g_m = m_dot[0]-g_dot[0]
            label = "X vector from G to M "+str(x_vector_g_m)
            cv2.putText(original, label, (0, 30+labels_top_margin), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))

            y_vector_g_m = m_dot[1]-g_dot[1]
            label = "Y vector from G to M "+str(y_vector_g_m)
            cv2.putText(original, label, (0, 45+labels_top_margin), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))
            # print("Point 3")
            labels_top_margin =+ 50


    if at_least_one_image_is_similar  is True:
        cv2.imwrite(image_output_dir + 'final/' + ntpath.basename(image_to_scan_path),original)
    # print("Point 4")
        print("Rilevated and angle of "+str(angle_r_s))

        return (angle_r_s, x_vector_g_m, y_vector_g_m)
    else:
        return None
