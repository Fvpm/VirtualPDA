"""
Currently coded for Python only, not coded to work with database


"""

from tkinter import *

#Managers (controllers)


class DatabaseManager(object):
    def __init__(self):
        """Initialize connection to mySQL database"""
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


class GUIManager(object):
    def __init__(self):
        self.currentWindow = None
        self.guiDict = {}

    def setManagers(self, _databaseManager, _userManager, _noteManager, _groupManager):
        """Because Managers have to be made all at once and reference each other, this function is called when this object is created on startup but after all managers are initalized"""
        self.userManager = _userManager
        self.databaseManager = _databaseManager
        self.groupManager = _groupManager
        self.noteManager = _noteManager
        self.managerList = [self.userManager , self.noteManager, self.groupManager, self, self.databaseManager]

    def startupGUI(self):
        self.root = Tk()
        self.root.withdraw()

        self.guiDict["login"] = LoginGUI(self.managerList, self.root)
        self.guiDict["register"] = RegisterGUI(self.managerList, self.root)

        self.openWindow("login")

        self.root.mainloop()

    def openWindow(self, keyword):
        if(self.currentWindow != None):
            self.currentWindow.hide()
        self.currentWindow = self.guiDict[keyword]
        self.currentWindow.show()
    def end(self):
        self.root.destroy()

#GUIs (view)

class AbstractGUI(object):
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
        self.window.deiconify()

    def hide(self):
        self.window.withdraw()
    def onClose(self):
        self.guiManager.end()


class LoginGUI(AbstractGUI):
    def __init__(self, managerList, parent):
        super().__init__(managerList, parent)

        self.window.geometry("600x400")

        buttonFrame = Frame(master=self.window, height=150, bg="red")
        buttonFrame.pack(fill=BOTH, side=BOTTOM, expand=True)

        labelFrame = Frame(master=self.window, height=250, bg="blue")
        labelFrame.pack(fill=BOTH, side=TOP, expand=True)
        
        registerButton = Button(buttonFrame, text = "register", command = self.register)
        registerButton.pack(side=BOTTOM)
        

    def register(self):
        self.guiManager.openWindow("register")


class RegisterGUI(AbstractGUI):
    def __init__(self, managerList, parent):
        super().__init__(managerList, parent)
        self.window.geometry("400x700")

        

#Data Objects (model)


class DataObjects(object):
    def __init__(self, ident):
        self.id = ident
        self.update = False
        self.mark = False
        
class Note(DataObjects):
    
    def __init__(self, own, visib, made, mod, memo, eday, impor, name, col, repeat, tag):
        self.owner = own
        self.vis = [visib]
        self.dmade = made
        self.lmod = mod
        self.text = memo
        self.edate = eday
        self.imp = impor
        self.title = name
        self.color = col
        self.rep = repeat
        self.tags = [tag]
        
    def edit(self, entertext):
        """Currently only allows adding to text, will eventually allow for full editing of text"""
        self.text += entertext
        
    def delete(self):
        """delete the note"""
        
    def share(self, shareuser):
        """share note with other users"""
        self.vis.append(shareuser)
        
class User(DataObjects):
    def __init__(self, intuse, intpass):
        self.username = intuse
        self.password = intpass
        self.groups = []
        self.notes = []
        
    def changePass(self, newpassword):
        self.password = newpassword
        
    def checkPass(self, attempt):
        if attempt == self.password:
            return True
        else:
            return False
        
    def createNote(self, date, entry):
        newnote=Note(self.id, self, date, date, entry, "", 0, "", "", False, "")
        self.notes.append(newnote)
        
    def changeUser(self, newusername):
        self.username = newusername
        
    def joinGroup(self, group):
        """Join a group"""
        self.groups.append(group)
        
    def createGroup(self, groupname, desc):
        """Create a new group"""
        newgroup = Group(groupname, desc, self)
        self.groups.append(newgroup)
        
    def leaveGroup(self, groupid):
        self.groups.remove(groupid)
        
    def delete(self):
        """delete the user"""
    
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
        
    def delete(self):
        """Delete the group"""
