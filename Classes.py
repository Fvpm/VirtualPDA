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

        serviceId = 'VirtualPDACISS471JustinFelice'
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

        self.verifyDatabase(serviceId)

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

    def verifyDatabase(self, serviceId):
        """Checks that the database is in the correct format. Otherwise, it creates the database in the correct format."""
        try:
            self.cursor.execute("USE {}".format(serviceId))
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.createDatabase(serviceId)
            else:
                print("Incorrect database")
        
    def createDatabase(self, serviceId):
        """Creates all the tables in the database if there wasn't already a database"""
        TABLES = {}

        TABLES['users'] = (
            "CREATE TABLE 'users' ("
            " 'user_id' int(12) NOT NULL AUTO_INCREMENT,"
            " password"
            " username"
            " PRIMARY KEY('book_num')"
            ") ENGINE=InnoDB")
        TABLES['notes'] = (
            "CREATE TABLE 'notes' ("
            " 'note_id' int(12) NOT NULL AUTO_INCREMENT,"
            " 'user_id' int(12)"
            " date_made"
            " lastmod"
            " notedata"
            " date"
            " import"
            " title"
            " color"
            " repeat"
            " PRIMARY KEY('note_id')"
            " FOREIGN KEY('user_id') REFERENCES users(user_id)"
            ") ENGINE=InnoDB")
        TABLES['groupcon'] = (
            "CREATE TABLE 'usercon' ("
            " 'group_id' NOT NULL"
            " 'note_id' NOT NULL"
            " PRIMARY KEY('group_id', 'note_id')"
            ") ENGINE=InnoDB")
        TABLES['groups'] = (
            "CREATE TABLE 'groups' ("
            " 'group_id' int(12) NOT NULL AUTO_INCREMENT,"
            " name"
            " description"
            " 'user_id'"
            " PRIMARY KEY('book_num')"
            " FOREIGN KEY('user_id') REFERENCES users(user_id)"
            ") ENGINE=InnoDB")
        TABLES['groupmem'] = (
            "CREATE TABLE 'groupmem' ("
            " 'user_id' NOT NULL"
            " 'group_id' NOT NULL"
            " PRIMARY KEY('user_id', 'group_id')"
            ") ENGINE=InnoDB")
        TABLES['usercon'] = (
            "CREATE TABLE 'usercon' ("
            " 'user_id' NOT NULL"
            " 'note_id'"
            " PRIMARY KEY('user_id', 'note_id')"
            ") ENGINE=InnoDB")
        TABLES['tags'] = (
            "CREATE TABLE 'tags' ("
            " 'tag_id' int(12) NOT NULL AUTO_INCREMENT,"
            " tag_text"
            " 'note_id'"
            " PRIMARY KEY('tag_id')"
            " FOREIGN KEY('note_id') REFERENCES notes(note_id)"
            ") ENGINE=InnoDB")
        self.cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(serviceId))
        for table in TABLES:
            table_make = TABLES[table]
            try:
                self.cursor.execute(table_make)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print()
                else:
                    print(err.msg)

    def loadUsers(self):
        """Will load user data into self.userManager"""
        loadusers = ("SELECT * FROM users")
        self.cursor.execute(loadusers)
        load = self.cursor.fetchall()
        for user in load:
            if type(user[0]) is not int:
                user[0] = int(user[0])
            else:
                if type(user[1]) is not str:
                    user[1] = str(user[1])
                else:
                    if type(user[2]) is not str:
                        user[2] = str(user[2])
                    else:
                        self.userManager.newUser(user[0], user[1], user[2])

    def loadNotes(self):
        """Will load database data into self.noteManager"""
        pass

    def loadGroups(self):
        """Will load database data into self.groupManager"""
        pass
    
    def saveDatabase(self):
        """Saves and updates the database"""
        for User in self.userManager.userList:
            self.saveUsers(User)
        for Note in self.noteManager.noteList:
            self.saveNotes(Note)
        for Group in self.groupManager.groupList:
            self.saveGroups(Group)
        
    def saveUsers(self, user):
        modify_pass = ("UPDATE users"
                       "SET password = %s"
                       "WHERE user_id = %s")
        modify_user = ("UPDATE users"
                       "SET username = %s"
                       "WHERE user_id = %s")
        delete_user = ("DELETE FROM users WHERE user_id = %s")
        delete_usergroup=("DELETE FROM groupmem WHERE user_id = %s")
        delete_usernote=("DELETE FROM usercon WHERE user_id = %s")
        delete_usergrouping=("DELETE FROM groups WHERE user_id = %s")
        delete_usernotes=("DELETE FROM notes WHERE user_id = %s")
        add_newuser=("INSERT INTO users"
                     "(user_id, username, password)"
                     "VALUES (%(user_id)s, %(username)s, %(password)s)")
        if user.update == True:
            self.cursor.execute(modify_pass, user.password, user.id)
            self.cursor.execute(modify_user, user.username, user.id)
        elif user.mark == True:
            self.cursor.execute(delete_user, user.id)
            self.cursor.execute(delete_usergroup, user.id)
            self.cursor.execute(delete_usernote, user.id)
            self.cursor.execute(delete_usergrouping, user.id)
            self.cursor.execute(delete_usernotes, user.id)
        elif user.new == True:
            self.cursor.execute(add_newuser, user.id, user.username, user.password)
        
    def saveNotes(self, note):
        #Not fully implemented yet
        add_usercon = ("INSERT INTO usercon"
                        "(user_id, note_id)"
                        "VALUES (%(user_id)s, %(note_id)s)")
        delete_note = ("DELETE FROM notes WHERE note_id = %s")
        delete_notegroup=("DELETE FROM groupcon WHERE note_id = %s")
        delete_noteuser=("DELETE FROM usercon WHERE note_id = %s")
        delete_notetag=("DELETE FROM tags WHERE note_id = %s")
        remove_tag = ("DELETE FROM tags WHERE tag_id = %s AND note_id = %s")
        add_tag = ("INSERT INTO tags"
                   "(tag_id, tag_text, note_id)"
                   "VALUES (%(tag_id)s, %(tag_text)s, %(note_id)s)")
        update_notedata = ("UPDATE notes"
                        "SET notedata = %s"
                        "WHERE note_id = %s")
        update_notedate = ("UPDATE notes"
                        "SET lastmod = %s"
                        "WHERE note_id = %s")
        add_note = ("INSERT INTO notes"
                        "(note_id, user_id, date_made, lastmod, notedata, date, import, title, color, repeat)"
                        "VALUES (%(note_id)s, %(user_id)s, %(date_made)s, %(lastmod)s, %(notedata)s, %(date)s, %(import)s, %(title)s, %(color)s, %(repeat)s)")
        add_usercon = ("INSERT INTO usercon"
                        "(user_id, note_id)"
                        "VALUES (%(user_id)s, %(note_id)s)")
        if note.update == True:
            self.cursor.execute(add_usercon, shareuser, self.id)
            self.cursor.execute(remove_tag, oldtag[0], self.id)
            self.cursor.execute(add_tag, newtag, tagtext, self.id)
            self.cursor.execute(update_notedata, entertext, self.id)
            self.cursor.execute(update_notedate, datetime.now().date(), self.id)
            self.cursor.execute(add_note, noteid, self.id, date, date, entry, "", 5, "", "", False)
            self.cursor.execute(add_usercon, self.id, noteid)
        elif note.mark == True:
            self.cursor.execute(delete_note, self.id)
            self.cursor.execute(delete_notegroup, self.id)
            self.cursor.execute(delete_noteuser, self.id)
            self.cursor.execute(delete_notetag, self.id)
        
    def saveGroups(self, group):
        #Not fully implemented yet
        new_group = ("INSERT INTO groups"
                     "(group_id, name, description, user_id, privacy)"
                     "VALUES (%(group_id)s, %(name)s, %(description)s, %(user_id)s, %(privacy)s)")
        add_groupmem = ("INSERT INTO groupmem"
                        "(group_id, user_id)"
                        "VALUES (%(group_id)s, %(user_id)s)")
        add_groupcon = ("INSERT INTO groupcon"
                        "(group_id, note_id)"
                        "VALUES (%(group_id)s, %(note_id)s)")
        delete_group = ("DELETE FROM groups WHERE group_id = %s")
        delete_groupmem=("DELETE FROM groupmem WHERE group_id = %s")
        delete_groupnote=("DELETE FROM groupcon WHERE group_id = %s")
        modify_privacy = ("UPDATE groups"
                       "SET privacy = %s"
                       "WHERE group_id = %s")
        modify_name = ("UPDATE groups"
                       "SET name = %s"
                       "WHERE group_id = %s")
        remove_user=("DELETE FROM groupmem WHERE user_id = %s")
        modify_desc = ("UPDATE groups"
                       "SET description = %s"
                       "WHERE group_id = %s")
        remove_self=("DELETE FROM groupmem WHERE user_id = %s")
        if group.update == True:
            self.cursor.execute(new_group, groupid, groupname, desc, self.id, True)
            self.cursor.execute(add_groupmem, groupid, self.id)
            self.cursor.execute(add_groupcon, groupid, noteid)
            self.cursor.execute(remove_self, self.id)
            self.cursor.execute(modify_desc, newdesc, self.id)
            self.cursor.execute(remove_user, memind)
            self.cursor.execute(modify_name, newname, self.id)
            self.cursor.execute(modify_privacy, self.isPrivate, self.id)
        elif group.mark == True:
            self.cursor.execute(delete_group, self.id)
            self.cursor.execute(delete_groupmem, self.id)
            self.cursor.execute(delete_groupnote, self.id)

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
        """This is run once to start up tkinter. It creates all windows as Toplevels that are children of a perepetually unused Tk, and then starts with opening the login window."""
        self.root = Tk()
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

        registerButton = Button(buttonFrame, text = "Register", command = self.register)
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
    def __init__(self, ident):
        self.id = ident
        self.update = False
        self.mark = False


class Note(DataObjects):
    
    def __init__(self, ident, own, visib, made, mod, memo, eday, impor, name, col, repeat, tag):
        super().__init__(ident)
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
    def __init__(self, ident, intuse, intpass):
        super().__init__(ident)
        self.username = intuse
        self.password = intpass
        self.groups = []
        self.notes = []
        self.new = False
        
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
    def __init__(self, ident, groupname, desc, own):
        super().__init__(ident)
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
