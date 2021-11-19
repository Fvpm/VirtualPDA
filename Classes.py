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

        #MySql Login
        self.serviceId = 'VirtualPDA' 
        sqlUsername = keyring.get_password(self.serviceId, self.serviceId)
        if(sqlUsername is None): #First time running program.
            sqlUsername = input("Enter in mysql server username: ")
            sqlPassword = getpass.getpass()
        else:
            sqlPassword = keyring.get_password(self.serviceId, sqlUsername)
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
        keyring.set_password(self.serviceId, self.serviceId, sqlUsername)
        keyring.set_password(self.serviceId, sqlUsername, sqlPassword)
        
        #Database
        self.cursor = self.database.cursor(buffered=True)
        #self.cursor.execute("DROP DATABASE {};".format(self.serviceId))
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
        #self.loadNotes()
        #self.loadGroups()
        return [self.userManager, self.noteManager, self.groupManager, self.guiManager]

    def verifyDatabase(self):
        """Checks that the database is in the correct format. Otherwise, it creates the database in the correct format."""
        """Precondition: MySQL is installed on computer
        Postcondition: VirtualPDA database should be on computer and accessed"""
        try:
            self.cursor.execute("USE {}".format(self.serviceId))
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
            self.cursor.fetchall()
            print("Accessed")
        except mysql.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.createDatabase(self.serviceId)
            else:
                self.cursor.execute("DROP DATABASE;")
                self.createDatabase(self.serviceId)
        
    def createDatabase(self, serviceId):
        """Creates all the tables in the database if there wasn't already a database"""
        """Precondition: MySQL is installed on computer
        Postcondition: VirtualPDA database should be on computer"""
        TABLES = {}

        TABLES['users'] = (
            "CREATE TABLE `users` ("
            " `user_id` int(12) NOT NULL AUTO_INCREMENT,"
            " `username` varchar(16),"
            " `password` varchar(16),"
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
            " `note_id` int(12) NOT NULL,"
            " `tag_text` varchar(16),"
            " FOREIGN KEY(`note_id`) REFERENCES `notes` (`note_id`),"
            " PRIMARY KEY(`tag_id`, `note_id`)"
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
        """Precondition: There is data to be loaded
        Postcondition: Data should be loaded from database into program"""
        self.cursor.fetchall()
        loadusers = ("SELECT * FROM users")
        self.cursor.execute(loadusers)
        load = self.cursor.fetchall()
        print(load)
        for user in load:
            if type(user[0]) is not int:
                user[0] = int(user[0])
            if type(user[1]) is not str:
                user[1] = str(user[1])
            if type(user[2]) is not str:
                user[2] = str(user[2])
            self.userManager.addUser(user[0], user[1], user[2])

    def loadNotes(self):
        """Will load database data into self.noteManager"""
        """Precondition: There is data to be loaded
        Postcondition: Data should be loaded from database into program"""
        loadnotes = ("SELECT * FROM notes")
        self.cursor.execute(loadnotes)
        load = self.cursor.fetchall()
        for note in load:
            if type(note[0]) is not int:
                note[0] = int(note[0])
            if type(note[1]) is not int:
                note[1] = int(note[1])
            if type(note[2]) is not str:
                note[2] = str(note[2])
            if type(note[3]) is not str:
                note[3] = str(note[3])
            if type(note[4]) is not str:
                note[4] = str(note[4])
            if type(note[5]) is not str:
                note[5] = str(note[5])
            if type(note[6]) is not int:
                note[6] = int(note[6])
            if type(note[7]) is not str:
                note[7] = str(note[7])
            if type(note[8]) is not str:
                note[8] = str(note[8])
            if type(note[9]) is not str:
                note[9] = str(note[9])
            self.noteManager.addNote(note[0], note[1], note[2], note[3], note[4], note[5], note[6], note[7], note[8], note[9])

    def loadGroups(self):
        """Will load database data into self.groupManager"""
        """Precondition: There is data to be loaded
        Postcondition: Data should be loaded from database into program"""
        loadgroups = ("SELECT * FROM usergroups")
        self.cursor.execute(loadgroups)
        load = self.cursor.fetchall()
        for group in load:
            if type(group[0]) is not int:
                group[0] = int(group[0])
            if type(group[1]) is not str:
                group[1] = str(group[1])
            if type(group[2]) is not str:
                group[2] = str(group[2])
            if type(group[3]) is not int:
                group[3] = int(group[3])
            self.groupManager.addGroup(group[0], group[1], group[2], group[3])
    
    def saveDatabase(self):
        """Saves and updates the database"""
        """Precondition: There is data to be saved
        Postcondition: Data should be loaded from program into the database"""
        for User in self.userManager.userList:
            self.saveUsers(User)
            User.setNew(False)
            User.setUpdate(False)
        for Note in self.noteManager.noteList:
            self.saveNotes(Note)
            Note.setNew(False)
            Note.setUpdate(False)
        for Group in self.groupManager.groupList:
            self.saveGroups(Group)
            Group.setNew(False)
            Group.setUpdate(False)
        self.database.commit()
        
    def saveUsers(self, user):
        """Precondition: User ID is not 0. ID should be 12 digits long at max. Username and Password should be 16 characters long at max.
        Postcondition: User data should be saved to the database"""
        modify_pass = ("UPDATE users "
                       "SET password = %s "
                       "WHERE user_id = %s")
        modify_user = ("UPDATE users "
                       "SET username = %s "
                       "WHERE user_id = %s")
        delete_user = ("DELETE FROM users WHERE user_id = %s")
        delete_usergroup=("DELETE FROM groupmem WHERE user_id = %s")
        delete_usernote=("DELETE FROM usercon WHERE user_id = %s")
        delete_usergrouping=("DELETE FROM usergroups WHERE user_id = %s")
        delete_usernotes=("DELETE FROM notes WHERE user_id = %s")
        add_newuser=("INSERT INTO users"
                     "(user_id, username, password)"
                     "VALUES (%s, %s, %s)")
        if user.getNew() == True:
            self.cursor.execute(add_newuser, (user.getId(), user.getUsername(), user.getPassword()))
        elif user.getMark() == True:
            ident = (user.getId(), )
            self.cursor.execute(delete_user, ident)
            self.cursor.execute(delete_usergroup, ident)
            self.cursor.execute(delete_usernote, ident)
            self.cursor.execute(delete_usergrouping, ident)
            self.cursor.execute(delete_usernotes, ident)
        elif user.getUpdate() == True:
            self.cursor.execute(modify_pass, (user.password, user.getId()))
            self.cursor.execute(modify_user, (user.username, user.getId()))
        
    def saveNotes(self, note):
        """Precondition: Note ID is not 0. Note ID and User ID are 12 digits long at max. Importance is two digits long at max. Title is 15 characters long at max. Color is 10 characters long at max.
        Postcondition: Note data should be saved to the database"""
        add_usercon = ("INSERT INTO usercon"
                        "(user_id, note_id)"
                        "VALUES (%s, %s)")
        delete_note = ("DELETE FROM notes WHERE note_id = %s")
        delete_notegroup=("DELETE FROM groupcon WHERE note_id = %s")
        delete_noteuser=("DELETE FROM usercon WHERE note_id = %s")
        delete_notecon=("DELETE FROM usercon WHERE note_id = %s AND user_id = %s")
        delete_notetag=("DELETE FROM tags WHERE note_id = %s")
        remove_tag = ("DELETE FROM tags WHERE tag_id = %s AND note_id = %s")
        add_tag = ("INSERT INTO tags"
                   "(tag_id, tag_text, note_id)"
                   "VALUES (%s, %s, %s)")
        update_notedata = ("UPDATE notes "
                        "SET notedata = %s "
                        "WHERE note_id = %s")
        update_notedate = ("UPDATE notes "
                        "SET lastmod = %s "
                        "WHERE note_id = %s")
        add_note = ("INSERT INTO notes"
                        "(note_id, user_id, date_made, lastmod, notedata, date, import, title, color, repeating)"
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        add_usercon = ("INSERT INTO usercon"
                        "(user_id, note_id)"
                        "VALUES (%s, %s)")
        if note.getNew() == True:
            self.cursor.execute(add_note, note.getId(), note.getOwner(), note.getDateMade(), note.getModified(), note.getText(), note.getEvent(), note.getImportance(), note.getTitle(), note.getColor(), note.getRepeating())
            self.cursor.execute(add_usercon, note.getId(), note.getOwner())
        elif note.getMark() == True:
            ident = (note.getId(), )
            self.cursor.execute(delete_note, ident)
            self.cursor.execute(delete_notegroup, ident)
            self.cursor.execute(delete_noteuser, ident)
            self.cursor.execute(delete_notetag, ident)
        elif note.getUpdate() == True:
            tags = note.getTags()
            oldtags = note.getOldTags()
            for tag in tags:
                count = 0
                for oldtag in oldtags:
                    if tag == oldtag:
                        count += 1
                if count == 0:
                    self.cursor.execute(add_tag, tag[0], tag[1], note.getId())
            
            count = oldtags.length()
            for oldtag in oldtags:
                count = 0
                for tag in tags:
                    if oldtag == tag:
                        count += 1
                if count == 0:
                    self.cursor.execute(remove_tag, oldtag[0], note.getId())
            
            for shareuser in note.getVisibility():
                count = 0
                for olduser in note.getOldVisibility():
                    if shareuser == olduser:
                        count += 1
                if count == 0:    
                    self.cursor.execute(add_usercon, shareuser, note.getId())
            
            for olduser in note.getOldVisibility():
                count = 0
                for shareuser in note.getVisibility():
                    if olduser == shareuser:
                        count += 1
                if count == 0:
                    conident = (note.getId(), olduser)
                    self.cursor.execute(delete_notecon, conident)
            self.cursor.execute(update_notedata, note.getText(), note.getId())
            self.cursor.execute(update_notedate, note.getModified(), note.getId())
        
    def saveGroups(self, group):
        #Not fully implemented yet
        """Precondition: Group ID is not 0. Group ID and User ID are 12 digits long at max. Name is 30 characters long at max. Description is 180 characters long at max.
        Postcondition: Group data should be saved to the database"""
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
        modify_privacy = ("UPDATE usergroups "
                       "SET privacy = %s "
                       "WHERE group_id = %s")
        modify_name = ("UPDATE usergroups "
                       "SET name = %s "
                       "WHERE group_id = %s")
        remove_user=("DELETE FROM groupmem WHERE user_id = %s AND group_id = %s")
        modify_desc = ("UPDATE usergroups "
                       "SET description = %s "
                       "WHERE group_id = %s")
        if group.getNew() == True:
            self.cursor.execute(new_group, group.getId(), group.getName(), group.getDescription(), group.getOwner(), group.getPrivacy())
            for member in group.getMembers():
                self.cursor.execute(add_groupmem, group.getId(), member)
        elif group.getMark() == True:
            ident = (group.getId, )
            self.cursor.execute(delete_group, ident)
            self.cursor.execute(delete_groupmem, ident)
            self.cursor.execute(delete_groupnote, ident)
        elif group.getUpdate() == True:
            #self.cursor.execute(add_groupmem, group.id, self.id)
            #self.cursor.execute(add_groupcon, groupid, noteid)
            self.cursor.execute(modify_desc, group.getDescription(), group.getId())
            #self.cursor.execute(remove_user, memind)
            self.cursor.execute(modify_name, group.getName(), group.getId())
            self.cursor.execute(modify_privacy, group.getPrivacy(), group.getId())

class UserManager(object):
    def __init__(self):
        self.userList = []
        self.currentUser = None
        self.nextId = 1
    def setManagers(self, _databaseManager, _groupManager, _noteManager, _guiManager):
        """Because Managers have to be made all at once and reference each other, this function is called when this object is created on startup but after all managers are initalized"""
        self.databaseManager = _databaseManager
        self.userManager = _groupManager
        self.noteManager = _noteManager
        self.guiManager = _guiManager

    def login(self, username, password):
        """Searches for user with username and checks validity of password. Returns True if success and False if any type of failure (username not found / password invalid)"""
        for user in self.userList:
            if username == user.getUsername() and password == user.getPassword():
                currentUser = user
                return True
        return False

    def newUser(self, username, password):
        user = self.addUser(self.nextId, password, username)
        user.setNew(True)
    def addUser(self, userId, password, username):
        if(userId >= self.nextId):
            self.nextId = userId + 1
        newUser = User(userId, username, password)
        self.userList.append(newUser)
        return newUser
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
        self.databaseManager.saveDatabase()


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
        print(success)
        print("580")
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

        usernameLabel = Label(self.window, text = "Username:")
        passwordLabel = Label(self.window, text = "Password:")
        confirmPasswordLabel = Label(self.window, text = "Confirm Password:")
        registerButton = Button(self.window, text = "Register", command = self.newUser)

        self.usernameEntry = Entry(self.window)
        self.passwordEntry = Entry(self.window)
        self.confirmPasswordEntry = Entry(self.window)

        usernameLabel.pack()
        self.usernameEntry.pack()
        passwordLabel.pack()
        self.passwordEntry.pack()
        confirmPasswordLabel.pack()
        self.confirmPasswordEntry.pack()

        registerButton.pack()

    def newUser(self):
        #TODO confirm password
        username = self.usernameEntry.get()
        password = self.passwordEntry.get()
        self.userManager.newUser(username, password)
        self.backToLogin()

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
        userMenu.add_command(label="Logout", command=None)
        userMenu.add_command(label="Change Password", command = None)
        userMenu.add_command(label="Groups",command = None)
        self.menubar.add_cascade(label="User", menu=userMenu)

        memoMenu = Menu(self.menubar, tearoff=0)
        memoMenu.add_command(label="New", command=None)
        memoMenu.add_command(label="Search", command=None)
        memoMenu.add_command(label="Delete", command=None)
        memoMenu.add_command(label="Share", command=None)
        self.menubar.add_cascade(label="Memo", menu=memoMenu)

        self.window.config(menu=self.menubar)

    def show(self):
        super().show()
        #self.window.config(menu=self.menubar)

    def hide(self):
        super().hide()
        #self.window.config(menu=self.emptyMenubar)

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
        pass


#Data Objects (model)



class DataObjects(object):
    def __init__(self, _id):
        """Precondition: _id is not 0
        Postcondition: Child object is initialized"""
        self.id = _id
        self.update = False
        self.mark = False
        self.new = False
        
    def getId(self) -> int:
        """Returns self.id, an Integer representing a unique UserID"""
        return self.id
        
    def getUpdate(self):
        return self.update
        
    def getMark(self):
        return self.mark
        
    def getNew(self):
        return self.new
    
    def setId(self, nId):
        self.id = nId
    
    def setUpdate(self, change: bool):
        self.update = change
        
    def setMark(self):
        self.mark = True
        
    def setNew(self, change: bool):
        self.new = change


class Note(DataObjects):
    
    def __init__(self, _id: int, _owner, _dateMade: str, _lastModified: str, _text: str, _eventDate: str,
                 _importance: int, _title: str, _color: str, _repeating: str):
        """Precondition: _id is not 0. _owner is not 0.
        Postcondition: Note object is initialized"""
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
        self.text = entertext
        
    def share(self, shareuser):
        """share note with other users"""
        self.visibleBy.append(shareuser)
        
    def getOwner(self):
        return self.owner
    
    def getDateMade(self):
        return self.dateMade
    
    def getModified(self):
        return self.lastModified
    
    def getText(self):
        return self.text
    
    def getEvent(self):
        return self.eventDate
    
    def getImportance(self):
        return self.importance
    
    def getTitle(self):
        return self.title
    
    def getColor(self):
        return self.color
    
    def getRepeating(self):
        return self.repeating
    
    def getTags(self):
        return self.tags
    
    def getVisibility(self):
        return self.visibleBy
    
    def setOwner(self, nOwner):
        self.owner = nOwner
    
    def setDateMade(self, nDate):
        self.dateMade = nDate
    
    def setModified(self, nModified):
        self.lastModified = nModified
    
    def setEvent(self, nEvent):
        self.eventDate = nEvent
    
    def setImportance(self, nImportance):
        self.importance = nImportance
    
    def setTitle(self, nTitle):
        self.title = nTitle
    
    def setColor(self, nColor):
        self.color = nColor
    
    def setRepeating(self, nRepeating):
        self.repeating = nRepeating
    
    def setTags(self, nTags):
        self.tags = nTags
    
    def setVisibility(self, nVisibility):
        self.visibleBy = nVisibility


class User(DataObjects):
    def __init__(self, _id: int, _username: str, _password: str):
        """Groups and notes are filled in separately by userManager when appropriate"""
        """Precondition: _id is not 0
        Postcondition: User object is initialized"""
        super().__init__(_id)
        self.username = _username
        self.password = _password
        self.groups = []
        self.notes = []

    def getUsername(self) -> str:
        """Returns username, a string identifier for the user object"""
        return self.username

    def getGroups(self) -> list:
        """Returns a list of group objects the user is a part of"""
        return self.groups

    def getNotes(self) -> list:
        """Returns a list of note objects the user has access to"""
        return self.notes

    def getPassword(self) -> str:
        return self.password
    
    def setGroups(self, nGroups):
        self.groups = nGroups

    def setNotes(self, nNotes):
        self.notes = nNotes
        
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
    def __init__(self, _id, _groupname, _desc, _own):
        """Precondition: _id is not 0. _owner is not 0
        Postcondition: Group object is initialized"""
        super().__init__(_id)
        self.name = _groupname
        self.description = _desc
        self.owner = _own
        self.isPrivate = True
        self.members = [_own]
        
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
            
    def getName(self):
        return self.name
    
    def getDescription(self):
        return self.description
    
    def getOwner(self):
        return self.owner
    
    def getPrivacy(self):
        return self.isPrivate
    
    def getMembers(self):
        return self.members
    
    def setName(self, nName):
        self.name = nName
    
    def setDescription(self, nDescription):
        self.description = nDescription
    
    def setOwner(self, nOwner):
        self.owner = nOwner
    
    def setPrivacy(self, nPrivate):
        self.isPrivate = nPrivate
    
    def setMembers(self, nMembers):
        self.members = nMembers

def main():
    dbManager = DatabaseManager()
    managerList = dbManager.startup()
    userManager = managerList[0]
    noteManager = managerList[1]
    groupManager = managerList[2]
    guiManager = managerList[3]
    guiManager.startupGUI()

if __name__ == "__main__":
    main()
