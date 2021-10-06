
#This file contains all the class pertaining to GUI for our program. Every window has a separate class described in here

from tkinter import *

class GUIManager(object):
    def __init__(self):
        self.currentWindow = ""


class AbstractGUI(object):
    def __init__(self, managerList):
        self.userManager = managerList[0]
        self.noteManager = managerList[1]
        self.groupManager = managerList[2]
        self.guiManager = managerList[3]
        self.databaseManager = managerList[4]


class LoginGUI(AbstractGUI):
    def __init__(self, managerList):
        super.__init__(managerList)
        self.window = Tk()
        self.window.geometry("600x400")

        buttonFrame = Frame(master=self.window, height=150, bg="red")
        buttonFrame.pack(fill=BOTH, side=BOTTOM, expand=True)

        labelFrame = Frame(master=self.window, height=250, bg="blue")
        labelFrame.pack(fill=BOTH, side=TOP, expand=True)

        
        self.window.mainloop()

    def loginRequest(self):
        #TODO sends validity check to UserManager. Popup appears if failure, otherwise this window closes and MainGUI
        pass

#class registerGUI(object):
#    def __init__(self):
        

theLoginGUI = LoginGUI()
