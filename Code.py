import cv2
import math
import time
import numpy as np
import pyautogui as pg
cam = cv2.VideoCapture(0)
keypoints=[0,4,5,8,9,12,13,16,17,20]
train=True
tol=15
count=0
knowngesture=[]
# numgest=int(input('enter no.of gestures: '))
numgest=3
gestnames=["prev","pause","next"]
# for i in range(numgest):
#     x=input(f"enter name of gest:{i+1}: ")
#     gestnames.append(x)
# print(gestnames)
w, h = 640, 480
class Handmarks:
    import mediapipe as mp
    def __init__(self,hc=2,tol1=.7,tol2=.7):
        self.hands=self.mp.solutions.hands.Hands(False,hc,min_detection_confidence=tol1,min_tracking_confidence=tol2)
        self.h_draw=self.mp.solutions.drawing_utils
    def h_marks(self,val):
        valbgr=cv2.cvtColor(val,cv2.COLOR_RGB2BGR)
        hand_marks=[]
        results=self.hands.process(valbgr)
        if results.multi_hand_landmarks !=None:
            for marks in results.multi_hand_landmarks:
                self.h_draw.draw_landmarks(val,marks,self.mp.solutions.hands.HAND_CONNECTIONS)
                hand_mark=[]
                for mark in marks.landmark:
                    hand_mark.append((int(mark.x*w),int(mark.y*h)))
            hand_marks.append(hand_mark)
        return hand_marks
def finddistances(handdata):
    distmatrix=np.zeros((len(handdata),len(handdata)),dtype='float')
    palm_size=((handdata[0][0]-handdata[9][0])**2+(handdata[0][1]-handdata[9][1])**2)
    for i in range(len(handdata)):
        for j in range(len(handdata)):
            distmatrix[i][j]=math.sqrt(((handdata[i][0]-handdata[j][0])**2+(handdata[i][1]-handdata[j][1])**2)/palm_size)
    return distmatrix
def find_error(knownmatrix,unknownmatrix,keypoints):
    error=0
    for i in keypoints:
        for j in keypoints:
            error+=abs(knownmatrix[i][j]-unknownmatrix[i][j])
    print(error)
    return error
def findgesture(unknowngest,knowngest,keypoints,tol,gestnames):
    errorarray=[]
    for i in range(len(gestnames)):
        error=find_error(knowngest[i],unknowngest,keypoints)
        errorarray.append(error)
    errormin=errorarray[0]
    minindex=0
    for i in range(len(errorarray)):
        if errorarray[i]<errormin:
            errormin=errorarray[i]
            minindex=i
        if errormin<tol:
            gesture=gestnames[minindex]
        else:
            gesture='UNKNOWN'
    return gesture
def gesture_control(gesture):
    if gesture == gestnames[0]:
        pg.click(673,778)
    if gesture == gestnames[1]:
        pg.click(766,782)
    if gesture == gestnames[2]:
        pg.click(720,780)
    if gesture == 'UNKNOWN':
        print('YOU GAVE AN UNKNOWN GESTURE')
handmarks=Handmarks()
time.sleep(5)
while 1:
    ig,frame=cam.read()
    marks=handmarks.h_marks(frame)
    if train==True:
        if marks !=[]:
            print(f"show gesture for {gestnames[count]} press t to continue")
            if cv2.waitKey(1) & 0xff==ord('t'):
                knownmartix=finddistances(marks[0])
                knowngesture.append(knownmartix)
                count+=1
                if count==numgest:
                    train=False
    if train==False:
        if marks !=[]:
            unknownmartix=finddistances(marks[0])
            find_gesture=findgesture(unknownmartix,knowngesture,keypoints,tol,gestnames)
            cv2.putText(frame,find_gesture,(int(w/2),int(h/2)),cv2.FONT_HERSHEY_PLAIN,1,(0,255,0),1)
            gesture_control(find_gesture)
    # for mark in marks:
        # for i in keypoints:
            # cv2.circle(frame,mark[i],5,(255,0,0),2)
    cv2.imshow('cam',frame)
    if cv2.waitKey(1) & 0xff==ord('q'):
        break
cam.release()
cv2.destroyAllWindows()
