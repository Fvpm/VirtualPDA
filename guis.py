from tkinter import *

class GUIManager(object):
    def __init__(self):
        self.currentWindow = None
        self.guiDict = {}
        self.root = Tk()
    def setManagers(self, _databaseManager, _userManager, _noteManager, _groupManager):
        """Because Managers have to be made all at once and reference each other, this function is called when this object is created on startup but after all managers are initalized"""
        self.userManager = _userManager
        self.databaseManager = _databaseManager
        self.groupManager = _groupManager
        self.noteManager = _noteManager
        self.managerList = [self.userManager , self.noteManager, self.groupManager, self, self.databaseManager]
    def startupGUI(self):
        """This is run once to start up tkinter. It creates all windows as Toplevels that are children of a perepetually unused Tk, and then starts with opening the login window."""
        self.root.withdraw()

        self.guiDict["login"] = LoginGUI(self.managerList, self.root)
        self.guiDict["register"] = RegisterGUI(self.managerList, self.root)
        self.guiDict["home"] = HomeGUI(self.managerList, self.root)

        self.openWindow("login")

        self.root.mainloop()

    def openWindow(self, keyword):
        """Switches windows by hiding the current one and showing the requested"""
        if(self.currentWindow != None):
            self.currentWindow.hide()

        if(keyword in self.guiDict.keys()):
            self.currentWindow = self.guiDict[keyword]
            self.currentWindow.show()
        else:
            #This shouldn't ever print in production but if it does it should be helpful.
            print("Incorrect keyword sent to guiManager.openWindow(keyword) . Incorrect keyword: \"" + keyword + "\" not found in guiDict")

        
    def end(self):
        """Ends the tkinter program. Is called when x on any window is pressed"""
        self.root.destroy()
    
    def popup(self, text):
        """Creates a simple popup with "ok" to close"""
        #TODO
        pass


class AbstractGUI(object):
    """Parent class of all main GUI windows. Does not include popups"""
    def __init__(self, managerList, parent):
        self.userManager = managerList[0]
        self.noteManager = managerList[1]
        self.groupManager = managerList[2]
        self.guiManager = managerList[3]
        self.databaseManager = managerList[4]
        self.window = Toplevel()
        self.window.withdraw()
        self.window.protocol("WM_DELETE_WINDOW",self.onClose)

    def show(self):
        """Makes window re-appear if invisible. Does nothing if visible"""
        self.window.deiconify()

    def hide(self):
        """Makes window disppear if visible. Does not destroy window or data within it, just visually removes it from the screen"""
        self.window.withdraw()

    def onClose(self):
        """Closing any window using the system's red X will close the program. This is a helper function for the event handler set up in __init__ in order to do so."""
        self.guiManager.end()


class LoginGUI(AbstractGUI):
    def __init__(self, managerList, parent):
        """Creates the window and all its widgets."""
        super().__init__(managerList, parent)

        self.window.geometry("600x400")

        buttonFrame = Frame(master=self.window, height=150, bg="red")
        buttonFrame.pack(fill=BOTH, side=BOTTOM, expand=True)

        entryFrame = Frame(master=self.window, height=250, bg="blue")
        entryFrame.pack(fill=BOTH, side=TOP, expand=True)

        registerButton = Button(buttonFrame, text = "Register", command = self.openRegisterWindow)
        registerButton.pack()
        loginButton = Button(buttonFrame, text = "Login", command = self.login)
        loginButton.pack()
        guestButton = Button(buttonFrame, text = "Guest", command = self.guestLogin)
        guestButton.pack()

        usernameFrame = Frame(entryFrame)
        usernameFrame.pack()
        usernameLabel = Label(usernameFrame, text = "Username:")
        usernameLabel.pack(side=LEFT)
        self.usernameEntry = Entry(usernameFrame)
        self.usernameEntry.pack(side=RIGHT)

        passwordFrame = Frame(entryFrame)
        passwordFrame.pack()
        passwordLabel = Label(passwordFrame, text = "Password:")
        passwordLabel.pack(side=LEFT)
        self.passwordEntry = Entry(passwordFrame)
        self.passwordEntry.pack(side=RIGHT)
    def openRegisterWindow(self):
        """Opens the register window, which will set loginGUI to invisible"""
        self.guiManager.openWindow("register")

    def login(self):
        """Sends a login request to userManager. Logs user in and brings them to home if success, displays a popup if unsuccessful"""
        self.guiManager.openWindow("home")
        """
        username = self.usernameEntry.get()
        password = self.passwordEntry.get()
        success = self.userManager.login(username,password)
        if success:
            self.guiManager.openWindow("home")
        else:
            self.guiManager.popup("Incorrect Username and Password")
        """
    def guestLogin(self):
        
        pass


class RegisterGUI(AbstractGUI):
    def __init__(self, managerList, parent):
        super().__init__(managerList, parent)
        self.window.geometry("400x700")
        
        backButton = Button(self.window, text = "<-", command = self.backToLogin)
        backButton.pack(side = TOP, anchor = "nw")

        usernameLabel = Label(self.window, text = "Username:")
        passwordLabel = Label(self.window, text = "Password:")
        confirmPasswordLabel = Label(self.window, text = "Confirm Password:")

        self.usernameEntry = Entry(self.window)
        self.passwordEntry = Entry(self.window)
        self.confirmPasswordEntry = Entry(self.window)

        usernameLabel.pack()
        self.usernameEntry.pack()
        passwordLabel.pack()
        self.passwordEntry.pack()
        confirmPasswordLabel.pack()
        self.confirmPasswordEntry.pack()

    def backToLogin(self):
        self.guiManager.openWindow("login")

class HomeGUI(AbstractGUI):
    def __init__(self, managerList, parent):
        super().__init__(managerList, parent)
        self.window.geometry("800x600")

        backButton = Button(self.window, text = "<-", command = self.backToLogin)
        backButton.pack(side = TOP, anchor = "nw")

        self.menubar = Menu(self.window)
        self.emptyMenubar = Menu(self.window)

        userMenu = Menu(self.menubar, tearoff=0)
        userMenu.add_command(label="Logout", command=self.backToLogin)
        userMenu.add_command(label="Change Password", command = self.openPasswordChangeWindow)
        userMenu.add_command(label="Groups",command = self.openGroupsWindow)
        self.menubar.add_cascade(label="User", menu=userMenu)

        memoMenu = Menu(self.menubar, tearoff=0)
        memoMenu.add_command(label="New", command=self.createNewFile)
        memoMenu.add_command(label="Search", command=self.openSearchWindow)
        memoMenu.add_command(label="Delete", command=self.deleteCurrentFile)
        memoMenu.add_command(label="Share", command=self.openShareWindow)
        self.menubar.add_cascade(label="Memo", menu=memoMenu)

    def show(self):
        super().show()
        self.window.config(menu=self.menubar)

    def hide(self):
        super().hide()
        self.window.config(menu=self.emptyMenubar)

    def openShareWindow(self):
        pass

    def deleteCurrentFile(self):
        pass

    def openSearchWindow(self):
        pass

    def createNewFile(self):
        pass

    def backToLogin(self):
        self.guiManager.openWindow("login")

    def openPasswordChangeWindow(self):
        """open a window that doesnt exist yet"""
        pass

    def openGroupsWindow(self):
        """open the groups window popup"""
        pass



if __name__ == "__main__":
    guiManager = GUIManager()
    guiManager.setManagers(1,2,3,4)
    guiManager.startupGUI()
