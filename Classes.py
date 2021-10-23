"""
Currently coded for Python only, not coded to work with database
"""
from tkinter import *
import mysql.connector as mysql
from mysql.connector import errorcode
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
        
        self.cursor = self.database.cursor(buffered=True)
        
        #self.cursor.execute("DROP DATABASE {}".format(serviceId))
        #self.createDatabase(serviceId)
        self.verifyDatabase(serviceId)
        #Code placed here for testing purposes
        add_newuser=("INSERT INTO users"
                     "(user_id, password, username)"
                     "VALUES (%s, %s, %s)")
        self.cursor.execute(add_newuser, (1, "Alex", "x1pho3nc0rp"))
        self.startup()
        print(self.userManager.userList[0].username)
        print(self.userManager.userList[0].password)
        print(self.userManager.userList[0].id)
        #End of test purpose code

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
        #self.loadNotes()
        #self.loadGroups()
        return [self.userManager, self.noteManager, self.groupManager, self.guiManager]

    def verifyDatabase(self, serviceId):
        """Checks that the database is in the correct format. Otherwise, it creates the database in the correct format."""
        try:
            print(self.cursor.execute("USE {}".format(serviceId)))
            self.cursor.execute("SELECT user_id FROM users")
            self.cursor.execute("SELECT password FROM users")
            self.cursor.execute("SELECT username FROM users")
            self.cursor.execute("SELECT note_id FROM notes")
            self.cursor.execute("SELECT user_id FROM notes")
            self.cursor.execute("SELECT date_made FROM notes")
            self.cursor.execute("SELECT lastmod FROM notes")
            self.cursor.execute("SELECT notedata FROM notes")
            self.cursor.execute("SELECT date FROM notes")
            self.cursor.execute("SELECT import FROM notes")
            self.cursor.execute("SELECT title FROM notes")
            self.cursor.execute("SELECT color FROM notes")
            self.cursor.execute("SELECT repeating FROM notes")
            self.cursor.execute("SELECT group_id FROM groupcon")
            self.cursor.execute("SELECT note_id FROM groupcon")
            self.cursor.execute("SELECT group_id FROM usergroups")
            self.cursor.execute("SELECT name FROM usergroups")
            self.cursor.execute("SELECT description FROM usergroups")
            self.cursor.execute("SELECT user_id FROM usergroups")
            self.cursor.execute("SELECT group_id FROM groupmem")
            self.cursor.execute("SELECT user_id FROM groupmem")
            self.cursor.execute("SELECT user_id FROM usercon")
            self.cursor.execute("SELECT note_id FROM usercon")
            self.cursor.execute("SELECT tag_id FROM tags")
            self.cursor.execute("SELECT tag_text FROM tags")
            self.cursor.execute("SELECT note_id FROM tags")
            print(self.cursor.execute("SHOW DATABASES;"))
            print("Acessed")
        except mysql.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.createDatabase(serviceId)
            else:
                print(err)
                print("Incorrect database")
        
    def createDatabase(self, serviceId):
        """Creates all the tables in the database if there wasn't already a database"""
        TABLES = {}

        TABLES['users'] = (
            "CREATE TABLE `users` ("
            " `user_id` int(12) NOT NULL AUTO_INCREMENT,"
            " `password` varchar(16),"
            " `username` varchar(16),"
            " PRIMARY KEY(`user_id`)"
            ") ENGINE=InnoDB")
        TABLES['notes'] = (
            "CREATE TABLE `notes` ("
            " `note_id` int(12) NOT NULL AUTO_INCREMENT,"
            " `user_id` int(12),"
            " `date_made` date,"
            " `lastmod` date,"
            " `notedata` longtext,"
            " `date` date,"
            " `import` int(2),"
            " `title` varchar(15),"
            " `color` varchar(10),"
            " `repeating` boolean,"
            " PRIMARY KEY(`note_id`),"
            " FOREIGN KEY(`user_id`) REFERENCES `users` (`user_id`)"
            ") ENGINE=InnoDB")
        TABLES['usergroups'] = (
            "CREATE TABLE `usergroups` ("
            " `group_id` int(12) NOT NULL AUTO_INCREMENT,"
            " `name` varchar(30),"
            " `description` varchar(180),"
            " `user_id` int(12),"
            " PRIMARY KEY(`group_id`),"
            " FOREIGN KEY(`user_id`) REFERENCES `users` (`user_id`)"
            ") ENGINE=InnoDB")
        TABLES['groupcon'] = (
            "CREATE TABLE `groupcon` ("
            " `group_id` int(12) NOT NULL,"
            " `note_id` int(12) NOT NULL,"
            " FOREIGN KEY(`group_id`) REFERENCES `usergroups` (`group_id`),"
            " FOREIGN KEY(`note_id`) REFERENCES `notes` (`note_id`),"
            " PRIMARY KEY(`group_id`, `note_id`)"
            ") ENGINE=InnoDB")
        TABLES['groupmem'] = (
            "CREATE TABLE `groupmem` ("
            " `user_id` int(12) NOT NULL,"
            " `group_id` int(12) NOT NULL,"
            " FOREIGN KEY(`user_id`) REFERENCES `users` (`user_id`),"
            " FOREIGN KEY(`group_id`) REFERENCES `usergroups` (`group_id`),"
            " PRIMARY KEY(`user_id`, `group_id`)"
            ") ENGINE=InnoDB")
        TABLES['usercon'] = (
            "CREATE TABLE `usercon` ("
            " `user_id` int(12) NOT NULL,"
            " `note_id` int(12) NOT NULL,"
            " FOREIGN KEY(`user_id`) REFERENCES `users` (`user_id`),"
            " FOREIGN KEY(`note_id`) REFERENCES `notes` (`note_id`),"
            " PRIMARY KEY(`user_id`, `note_id`)"
            ") ENGINE=InnoDB")
        TABLES['tags'] = (
            "CREATE TABLE `tags` ("
            " `tag_id` int(12) NOT NULL AUTO_INCREMENT,"
            " `tag_text` varchar(16),"
            " `note_id` int(12),"
            " PRIMARY KEY(`tag_id`),"
            " FOREIGN KEY(`note_id`) REFERENCES `notes` (`note_id`)"
            ") ENGINE=InnoDB")
        self.cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(serviceId))
        self.cursor.execute("USE {}".format(serviceId))
        for table in TABLES:
            table_make = TABLES[table]
            try:
                self.cursor.execute(table_make)
            except mysql.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("Table already exists")
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
            self.userManager.addUser(user[0], user[1], user[2])

    def loadNotes(self):
        """Will load database data into self.noteManager"""
        loadnotes = ("SELECT * FROM notes")
        self.cursor.execute(loadnotes)
        load = self.cursor.fetchall()
        for note in load:
            if type(note[0]) is not int:
                note[0] = int(note[0])
            else:
                if type(note[1]) is not int:
                    note[1] = int(note[1])
                else:
                    if type(note[2]) is not str:
                        note[2] = str(note[2])
                    else:
                        if type(note[3]) is not str:
                            note[3] = str(note[3])
                        else:
                            if type(note[4]) is not str:
                                note[4] = str(note[4])
                            else:
                                if type(note[5]) is not str:
                                    note[5] = str(note[5])
                                else:
                                    if type(note[6]) is not int:
                                        note[6] = int(note[6])
                                    else:
                                        if type(note[7]) is not str:
                                            note[7] = str(note[7])
                                        else:
                                            if type(note[8]) is not str:
                                                note[8] = str(note[8])
                                            else:
                                                if type(note[9]) is not str:
                                                    note[9] = str(note[9])
            self.noteManager.addNote(note[0], note[1], note[2], note[3], note[4], note[5], note[6], note[7], note[8], note[9])

    def loadGroups(self):
        """Will load database data into self.groupManager"""
        loadgroups = ("SELECT * FROM usergroups")
        self.cursor.execute(loadgroups)
        load = self.cursor.fetchall()
        for group in load:
            if type(group[0]) is not int:
                group[0] = int(group[0])
            else:
                if type(group[1]) is not str:
                    group[1] = str(group[1])
                else:
                    if type(group[2]) is not str:
                        group[2] = str(group[2])
                    else:
                        if type(group[3]) is not int:
                            group[3] = int(group[3])
            self.groupManager.addGroup(group[0], group[1], group[2], group[3])
    
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
        delete_usergrouping=("DELETE FROM usergroups WHERE user_id = %s")
        delete_usernotes=("DELETE FROM notes WHERE user_id = %s")
        add_newuser=("INSERT INTO users"
                     "(user_id, password, username)"
                     "VALUES (%s, %s, %s)")
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
                        "VALUES (%s, %s)")
        delete_note = ("DELETE FROM notes WHERE note_id = %s")
        delete_notegroup=("DELETE FROM groupcon WHERE note_id = %s")
        delete_noteuser=("DELETE FROM usercon WHERE note_id = %s")
        delete_notetag=("DELETE FROM tags WHERE note_id = %s")
        remove_tag = ("DELETE FROM tags WHERE tag_id = %s AND note_id = %s")
        add_tag = ("INSERT INTO tags"
                   "(tag_id, tag_text, note_id)"
                   "VALUES (%s, %s, %s)")
        update_notedata = ("UPDATE notes"
                        "SET notedata = %s"
                        "WHERE note_id = %s")
        update_notedate = ("UPDATE notes"
                        "SET lastmod = %s"
                        "WHERE note_id = %s")
        add_note = ("INSERT INTO notes"
                        "(note_id, user_id, date_made, lastmod, notedata, date, import, title, color, repeating)"
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        add_usercon = ("INSERT INTO usercon"
                        "(user_id, note_id)"
                        "VALUES (%s, %s)")
        if note.update == True:
            #self.cursor.execute(add_usercon, shareuser, note.id) More work needed
            #self.cursor.execute(remove_tag, oldtag[0], note.id) Conditions needed
            #for tag in note.tags: Come back later
             #   self.cursor.execute(add_tag, newtag, tag, note.id)
            #self.cursor.execute(update_notedata, note.text, note.id) More work needed
            self.cursor.execute(update_notedate, note.lmod, note.id)
            #self.cursor.execute(add_note, note.id, self.id, date, date, entry, "", 5, "", "", False) More work needed
            #self.cursor.execute(add_usercon, self.id, noteid) More work needed
        elif note.mark == True:
            self.cursor.execute(delete_note, note.id)
            self.cursor.execute(delete_notegroup, note.id)
            self.cursor.execute(delete_noteuser, note.id)
            self.cursor.execute(delete_notetag, note.id)
        
    def saveGroups(self, group):
        #Not fully implemented yet
        new_group = ("INSERT INTO usergroups"
                     "(group_id, name, description, user_id, privacy)"
                     "VALUES (%s, %s, %s, %s, %s)")
        add_groupmem = ("INSERT INTO groupmem"
                        "(group_id, user_id)"
                        "VALUES (%s, %s)")
        add_groupcon = ("INSERT INTO groupcon"
                        "(group_id, note_id)"
                        "VALUES (%s, %s)")
        delete_group = ("DELETE FROM usergroups WHERE group_id = %s")
        delete_groupmem=("DELETE FROM groupmem WHERE group_id = %s")
        delete_groupnote=("DELETE FROM groupcon WHERE group_id = %s")
        modify_privacy = ("UPDATE usergroups"
                       "SET privacy = %s"
                       "WHERE group_id = %s")
        modify_name = ("UPDATE usergroups"
                       "SET name = %s"
                       "WHERE group_id = %s")
        remove_user=("DELETE FROM groupmem WHERE user_id = %s")
        modify_desc = ("UPDATE usergroups"
                       "SET description = %s"
                       "WHERE group_id = %s")
        remove_self=("DELETE FROM groupmem WHERE user_id = %s")
        if group.update == True:
            #self.cursor.execute(add_groupmem, group.id, self.id) More work needed
            #self.cursor.execute(add_groupcon, groupid, noteid) More work needed
            #self.cursor.execute(remove_self, self.id) More work needed
            self.cursor.execute(modify_desc, group.desc, group.id)
            #self.cursor.execute(remove_user, memind) More work needed
            self.cursor.execute(modify_name, group.name, group.id)
            self.cursor.execute(modify_privacy, group.isPrivate, group.id)
        elif group.mark == True:
            self.cursor.execute(delete_group, group.id)
            self.cursor.execute(delete_groupmem, group.id)
            self.cursor.execute(delete_groupnote, group.id)
        elif group.new == True:
            #self.cursor.execute(new_group, group.id, group.name, group.desc, self.id, True) More work needed
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
    def addNote(self, noteId, owner, dateMade, lastModified, text, eventDate, importance, title, color, repeating):
        newNote = Note(noteId, owner, dateMade, lastModified, text, eventDate, importance, title, color, repeating)
        self.noteList.append(newNote)


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
    def addGroup(self, groupId, groupname, description, owner):
        newGroup = Group(groupId, groupname, description, owner)
        self.groupList.append(newGroup)

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
        self.new = False


    def edit(self, entertext):
        """Currently only allows adding to text, will eventually allow for full editing of text"""
        self.text += entertext
        
    def delete(self):
        """delete the note"""
        
    def share(self, shareuser):
        """share note with other users"""
        self.vis.append(shareuser)
        
    def toggleNewNote(self):
        "Changes new from false to True"
        self.new = True


class User(DataObjects):
    def __init__(self, _id, _username, _password):
        """Groups and notes are filled in separately by userManager when appropriate"""
        super().__init__(_id)
        self.username = _username
        self.password = _password
        self.groups = []
        self.notes = []
        self.new = False

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
    def __init__(self, ident, groupname, desc, own):
        super().__init__(ident)
        self.name = groupname
        self.description = desc
        self.owner = own
        self.isPrivate = True
        self.members = [own]
        self.new = False
        
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

def main():
    dbManager = DatabaseManager()

main()