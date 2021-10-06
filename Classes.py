
#This file contains all the class pertaining to GUI for our program. Every window has a separate class described in here

from tkinter import *

class GUIManager(object):
    def __init__(self):
        self.currentWindow = ""

        

class LoginGUI(object):
    def __init__(self):
        window = Tk()
        window.geometry("600x400")

        buttonFrame = Frame(master=window, height=150, bg="red")
        buttonFrame.pack(fill=BOTH, side=BOTTOM, expand=True)

        labelFrame = Frame(master=window, height=250, bg="blue")
        labelFrame.pack(fill=BOTH, side=TOP, expand=True)




        loginButton = 
        
        window.mainloop()

    def loginRequest(self):
        #TODO sends validity check to UserManager. Popup appears if failure, otherwise this window closes and MainGUI

#class registerGUI(object):
#    def __init__(self):
        

theLoginGUI = LoginGUI()
