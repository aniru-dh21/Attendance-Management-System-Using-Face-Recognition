"""
Authors: Shreyas, Abhishek, Sathwik, Anirudh, Anvesh, Eshwar
Title: Attendance management system using face recognition
"""

#Importing required libraries
import face_recognition as fr
import cv2 as cv
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
import pymysql
from twilio.rest import Client 

#Declaring global variables
global present
present=[]

#Using tkinter to take target image input
Tk().withdraw()
load_image=askopenfilename()

#Loading the target image and getting encodings of all indivisual faces in it
target_image = fr.load_image_file(load_image)
target_encoding = fr.face_encodings(target_image)

#Encodings of individual faces from individual images
def encode_faces(folder):
    list_people_encodings = []
    for filename in os.listdir(folder):
        known_image = fr.load_image_file(f'{folder}{filename}')
        known_encoding = fr.face_encodings(known_image)[0]
        list_people_encodings.append((known_encoding, filename))
    return list_people_encodings

#Finding the faces in the group photo
def find_target_face():
    face_location=fr.face_locations(target_image)
    for person in encode_faces('Attendance2/'):
        encoded_face=person[0]
        filename=person[1]
        is_target_face=fr.compare_faces(encoded_face, target_encoding,tolerance=0.55)
        #print(f'{is_target_face} {filename}')
        if face_location:
            face_number=0
            for location in face_location:
                if is_target_face[face_number]:
                    label=filename
                    present.append(label)
                    create_frame(location, label)
                face_number+=1

#Creating a frame/box around the target face
def create_frame(location, label):
    top, right, bottom, left = location
    cv.rectangle(target_image, (left,top), (right, bottom),(255,0,0),2)
    cv.rectangle(target_image, (left, bottom+20), (right, bottom), (255, 0, 0), cv.FILLED)
    cv.putText(target_image,label,(left+3,bottom+14),cv.FONT_HERSHEY_DUPLEX,0.4,(255,255,255),1)

#Converting the bgr image to rgb
def render_image():
    rgb_img = cv.cvtColor(target_image, cv.COLOR_BGR2RGB)
    resize_img = cv.resize(rgb_img, (720,540))
    cv.imshow('Final Image', resize_img)
    cv.waitKey(0)

#Marking attendance in the database
def updating_attendance():
    connection = pymysql.connect(host='localhost',user='root',passwd='',database='mydatabase')
    cursor = connection.cursor()
    update_absent = "UPDATE `attendance` SET `Attendance`='Absent';"
    cursor.execute(update_absent)
    for i in present:
        update_present = "UPDATE `attendance` SET `Attendance`='Present' WHERE Filename='"+i+"';"
        cursor.execute(update_present)
    connection.commit()
    connection.close()

#Calling the functions
find_target_face()
render_image()
updating_attendance()


def fetching_absentees_phno():
    connection = pymysql.connect(host='localhost',user='root',passwd='',database='mydatabase')
    cursor = connection.cursor()
    select = "SELECT Phone FROM `attendance` WHERE Attendance='Absent';"
    cursor.execute(select)
    absentees_phno=cursor.fetchall()
    return absentees_phno

absentees_numbers = fetching_absentees_phno()

def sms(absentees_numbers):
    sid = "ACb1c059bb53d1256431ed1fec6f83e42c"
    auth_token = "a5706fd3cb1aa61feb1abd549eca8213"
    cl = Client(sid,auth_token)
    for phno in absentees_numbers:
        number=''.join(phno)
        cl.messages.create(body="absent message date-(13-10-22)", from_='+15742086691', to=number)

sms(absentees_numbers)
