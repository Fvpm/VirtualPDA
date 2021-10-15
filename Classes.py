"""
Currently coded for Python only, not coded to work with database
"""
from tkinter import *
import mysql.connector as mysql
import keyring
import getpass
import datetime

#Managers (controllers)



class DatabaseManager(object):
    def __init__(self):
        """Initialize connection to mySQL database. Prompts user for username and password to connect to "localhost" mysql server. Saves this username and password to the machine's keychain so that it only asks on first run."""

        serviceId = 'VirtualPDA'
        sqlUsername = keyring.get_password(serviceId, serviceId)

        if(sqlUsername is None): #First time running program.
            sqlUsername = input("Enter in mysql server username: ")
            sqlPassword = getpass.getpass()
        else:
            sqlPassword = keyring.get_password(serviceId, sqlUsername)
        
        unsuccessful = True
        while(unsuccessful):
            
            try:
                self.database = mysql.connect(
                    host = "localhost",
                    user = sqlUsername,
                    passwd = sqlPassword
                )
                unsuccessful = False

            except Exception as e:
                print(e)
                print("Incorrect username and password for localhost mysql server. Please try again.")
                sqlUsername = input("Enter in mysql server username: ")
                sqlPassword = getpass.getpass()
        keyring.set_password(serviceId, serviceId, sqlUsername)
        keyring.set_password(serviceId, sqlUsername, sqlPassword)

        self.cursor = self.database.cursor()

        self.verifyDatabase()

    def startup(self) -> list:
        """Creates managers and loads in their data from database. Returns list of [userManager, noteManager, groupManger, and guiManager]"""
        self.groupManager = GroupManager()
        self.userManager = UserManager()
        self.noteManager = NoteManager()
        self.guiManager = GUIManager()

        #set all managers to reference each other
        self.groupManager.setManagers(self, self.userManager, self.noteManager, self.guiManager)
        self.userManager.setManagers(self, self.groupManager, self.noteManager, self.guiManager)
        self.noteManager.setManagers(self, self.userManager, self.groupManager, self.guiManager)
        self.guiManager.setManagers(self, self.userManager, self.noteManager, self.groupManager)

        #load data from database
        self.loadUsers()
        self.loadNotes()
        self.loadGroups()
        return [self.userManager, self.noteManager, self.groupManager, self.guiManager]

    def verifyDatabase(self):
        """Checks that the database is in the correct format. Otherwise, it creates the database in the correct format."""

    def loadUsers(self):
        """Will load user data into self.userManager"""
        pass

    def loadNotes(self):
        """Will load database data into self.noteManager"""
        pass

    def loadGroups(self):
        """Will load database data into self.groupManager"""
        pass


class UserManager(object):
    def __init__(self):
        self.userList = []
        self.currentUser = None;
    def setManagers(self, _databaseManager, _groupManager, _noteManager, _guiManager):
        """Because Managers have to be made all at once and reference each other, this function is called when this object is created on startup but after all managers are initalized"""
        self.databaseManager = _databaseManager
        self.userManager = _groupManager
        self.noteManager = _noteManager
        self.guiManager = _guiManager
    def login(self, username, password):
        """Searches for user with username and checks validity of password. Returns True if success and False if any type of failure (username not found / password invalid)"""
        pass
    def addUser(self, userId, username, password):
        newUser = User(userId, username, password)
        self.userList.append(newUser)
    def userJoinGroup(self, user, group):
        if group not in user.getGroups():
            user.addGroup(group)
        if user not in group.getMembers():
            group.addMember(group)


class NoteManager(object):
    def __init__(self):
        self.noteList = []
    def setManagers(self, _databaseManager, _userManager, _groupManager, _guiManager):
        """Because Managers have to be made all at once and reference each other, this function is called when this object is created on startup but after all managers are initalized"""
        self.databaseManager = _databaseManager
        self.userManager = _userManager
        self.groupManager = _groupManager
        self.guiManager = _guiManager    


class GroupManager(object):
    def __init__(self):
        self.groupList = []
    def setManagers(self, _databaseManager, _userManager, _noteManager, _guiManager):
        """Because Managers have to be made all at once and reference each other, this function is called when this object is created on startup but after all managers are initalized"""
        self.databaseManager = _databaseManager
        self.userManager = _userManager
        self.noteManager = _noteManager
        self.guiManager = _guiManager
    def userJoinGroup(self, user, group):
        self.userManager.userJoinGroup(user,group)

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




#GUIs (view)




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

        userNameFrame = Frame(entryFrame)
        userNameFrame.pack()
        userNameLabel = Label(userNameFrame, text = "Username:")
        userNameLabel.pack(side=LEFT)
        self.userNameEntry = Entry(userNameFrame)
        self.userNameEntry.pack(side=RIGHT)

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
        userName = self.userNameEntry.get()
        password = self.passwordEntry.get()
        success = self.userManager.login(userName,password)
        if success:
            self.guiManager.openWindow("home")
        else:
            self.guiManager.popup("Incorrect Username and Password")

    def guestLogin(self):
        
        pass


class RegisterGUI(AbstractGUI):
    def __init__(self, managerList, parent):
        super().__init__(managerList, parent)
        self.window.geometry("400x700")
        
        backButton = Button(self.window, text = "<-", command = self.backToLogin)
        backButton.pack(side = TOP, anchor = "nw")

    def backToLogin(self):
        self.guiManager.openWindow("login")



#Data Objects (model)



class DataObjects(object):
    def __init__(self, _id):
        self.id = _id
        self.update = False
        self.mark = False


class Note(DataObjects):
    
    def __init__(self, _id: int, _owner, _dateMade: str, _lastModified: str, _text: str, _eventDate: str,
                 _importance: int, _title: str, _color: str, _repeating: str):
        super().__init__(_id)
        self.owner = _owner
        self.dateMade = _dateMade
        self.lastModified = _lastModified
        self.text = _text
        self.eventDate = _eventDate
        self.importance = _importance
        self.title = _title
        self.color = _color
        self.repeating = _repeating

        self.tags = []
        self.visibleBy = []

    def edit(self, entertext):
        """Currently only allows adding to text, will eventually allow for full editing of text"""
        self.text += entertext
        
    def delete(self):
        """delete the note"""
        
    def share(self, shareuser):
        """share note with other users"""
        self.vis.append(shareuser)


class User(DataObjects):
    def __init__(self, _id, _username, _password):
        """Groups and notes are filled in separately by userManager when appropriate"""
        super().__init__(_id)
        self.username = _username
        self.password = _password
        self.groups = []
        self.notes = []

    def getId(self) -> int:
        """Returns self.id, an Integer representing a unique UserID"""
        return self.id

    def getUsername(self) -> str:
        """Returns username, a string identifier for the user object"""
        return self.userName

    def getGroups(self) -> list:
        """Returns a list of group objects the user is a part of"""
        return self.groups

    def getNotes(self) -> list:
        """Returns a list of note objects the user has access to"""
        return self.notes

    def checkPassword(self, attempt: str) -> bool:
        """Returns True if password attempt is correct and False otherwise"""
        if attempt == self.password:
            return True
        else:
            return False
        
    def changePassword(self, oldPassword: str, newPassword: str):
        """Changes password if the old password is correct"""
        if(self.checkPassword(oldPassword)):
            self.password = newPassword 
        
    def changeUsername(self, newUsername):
        """Sets a new username"""
        self.username = newUsername
        
    def addGroup(self, group):
        """Join a group"""
        self.groups.append(group) 
        
    def removeGroup(self, group):
        """Remove group from group list"""
        self.groups.remove(group)

    def addNote(self, note):
        """Adds note to note list"""
        self.notes.append(note)

    def removeNote(self, note):
        """removes note from note list"""
        self.notes.remove(note)
        


class Group(DataObjects):
    def __init__(self, groupname, desc, own):
        self.name = groupname
        self.description = desc
        self.owner = own
        self.isPrivate = True
        self.members = [own]
        
    def addUser(self, newuser):
        self.members.append(newuser)
        
    def editDesc(self, newdesc):
        self.description = newdesc
        
    def remUser(self, memind):
        self.members.remove(memind)
        
    def editName(self, newname):
        self.name = newname
        
    def togglePrivacy(self):
        """Change the privacy setting of the group"""
        if (self.isPrivate == True):
            self.isPrivate == False
        else:
            self.isPrivate == True
