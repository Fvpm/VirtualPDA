from tkinter import *
from tkinter import ttk
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
        self.loadNotes()
        self.loadGroups()


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
            " `date_made` datetime,"
            " `lastmod` datetime,"
            " `notedata` longtext,"
            " `date` date,"
            " `import` int(2),"
            " `title` varchar(32),"
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
            " `privacy` boolean,"
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
        loadusers = ("SELECT * FROM users")
        self.cursor.execute(loadusers)
        load = self.cursor.fetchall()
        for user in load:
            userdata = []
            userdata.append(user[0])
            userdata.append(user[1])
            userdata.append(user[2])
            if type(userdata[0]) is not int:
                userdata[0] = int(userdata[0])
            if type(userdata[1]) is not str:
                userdata[1] = str(userdata[1])
            if type(userdata[2]) is not str:
                userdata[2] = str(userdata[2])
            self.userManager.addUser(userdata[0], userdata[1], userdata[2])

    def loadNotes(self):
        """Will load database data into self.noteManager"""
        """Precondition: There is data to be loaded
        Postcondition: Data should be loaded from database into program"""
        loadnotes = ("SELECT * FROM notes")
        loadtags = ("SELECT * FROM tags")
        loadcon = ("SELECT * FROM usercon")
        self.cursor.execute(loadnotes)
        load = self.cursor.fetchall()
        self.cursor.execute(loadtags)
        load2 = self.cursor.fetchall()
        self.cursor.execute(loadcon)
        load3 = self.cursor.fetchall()
        for note in load:
            notedata = []
            notedata.append(note[2].strftime("%Y-%m-%d %H:%M:%S"))
            notedata.append(note[3].strftime("%Y-%m-%d %H:%M:%S"))
            if note[5] is not None:
                notedata.append(note[5].strftime("%Y-%m-%d"))
            else:
                notedata.append(None)

            self.noteManager.addNote(note[0], note[1], notedata[0], notedata[1], note[4], notedata[2], note[6], note[7], note[8], note[9])
        for note in self.noteManager.noteList:
            #Connect tags with their notes
            for tag in load2:
                if tag[0] == note.getId():
                    tagdata = []
                    tagdata.append(tag[0])
                    tagdata.append(tag[1])
                    if type(tagdata[0]) is not int:
                        tagdata[0] = int(tagdata[0])
                    if type(tagdata[1]) is not str:
                        tagdata[1] = str(tagdata[1])
                    note.addTag([tagdata[0], tagdata[1]])
            note.fillOldTags()
            #Connect notes with users that can see them
            for con in load3:
                if con[1] == note.getId():
                    condata = con[0]
                    if type(condata) is not int:
                        condata = int(condata)
                    note.share(condata)
        

    def loadGroups(self):
        """Will load database data into self.groupManager"""
        """Precondition: There is data to be loaded
        Postcondition: Data should be loaded from database into program"""
        loadgroups = ("SELECT * FROM usergroups")
        loadmembers = ("SELECT * FROM groupmem")
        loadnotes = ("SELECT * FROM groupcon")
        self.cursor.execute(loadgroups)
        load = self.cursor.fetchall()
        self.cursor.execute(loadmembers)
        load2 = self.cursor.fetchall()
        self.cursor.execute(loadnotes)
        load3 = self.cursor.fetchall()
        for group in load:
            groupdata = []
            groupdata.append(group[0])
            groupdata.append(group[1])
            groupdata.append(group[2])
            groupdata.append(group[3])
            groupdata.append(group[4])
            if type(groupdata[0]) is not int:
                groupdata[0] = int(groupdata[0])
            if type(groupdata[1]) is not str:
                groupdata[1] = str(groupdata[1])
            if type(groupdata[2]) is not str:
                groupdata[2] = str(groupdata[2])
            if type(groupdata[3]) is not int:
                groupdata[3] = int(groupdata[3])
            if type(groupdata[4]) is not int:
                groupdata[4] = int(groupdata[4])
            self.groupManager.addGroup(groupdata[0], groupdata[1], groupdata[2], groupdata[3], groupdata[4])
        #Connect the groups with their members
        for group in self.groupManager.groupList:
            for user in load2:
                if user[1] == group.getId():
                    userdata = user[0]
                    if type(userdata) is not int:
                        userdata = int(userdata)
                    group.addUser(userdata)
            group.fillOldMembers()
            #Connect the groups with their notes
            for note in load3:
                if note[0] == group.getId():
                    notedata = note[1]
                    if type(notedata) is not int:
                        notedata = int(notedata)
                    group.addNote(notedata)
            group.fillOldNotes()
    
    def saveDatabase(self):
        """Saves and updates the database"""
        """Precondition: There is data to be saved
        Postcondition: Data should be loaded from program into the database"""
        #Cycle through and save all users
        for User in self.userManager.userList:
            self.saveUsers(User)
            User.setNew(False)
            User.setUpdate(False)
        #Cycle through and save all notes
        for Note in self.noteManager.noteList:
            self.saveNotes(Note)
            Note.setNew(False)
            Note.setUpdate(False)
        #Cycle through and save all groups
        for Group in self.groupManager.groupList:
            self.saveGroups(Group)
            Group.setNew(False)
            Group.setUpdate(False)
        #Commit changes made to the database
        self.database.commit()
        
    def saveUsers(self, user):
        """Saves all data concerning users to the database"""
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
            #If user is new then add them to the database
            self.cursor.execute(add_newuser, (user.getId(), user.getUsername(), user.getPassword()))
        elif user.getMark() == True:
            #If the user has been marked for deletion then delete all entries in the database related to user
            ident = (user.getId(), )
            self.cursor.execute(delete_user, ident)
            self.cursor.execute(delete_usergroup, ident)
            self.cursor.execute(delete_usernote, ident)
            self.cursor.execute(delete_usergrouping, ident)
            self.cursor.execute(delete_usernotes, ident)
        elif user.getUpdate() == True:
            #If the user needs to be updated then update the database as well
            self.cursor.execute(modify_pass, (user.password, user.getId()))
            self.cursor.execute(modify_user, (user.username, user.getId()))
        
    def saveNotes(self, note):
        """Saves all data concerning notes to the database"""
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
                   "(tag_id, tag_text, note_id) "
                   "VALUES (%s, %s, %s) ")
        update_notedata = ("UPDATE notes "
                        "SET notedata = %s "
                        "WHERE note_id = %s")
        update_notedate = ("UPDATE notes "
                        "SET lastmod = %s "
                        "WHERE note_id = %s")
        update_notecolor = ("UPDATE notes "
                         "SET color = %s "
                         "WHERE note_id = %s")
        update_noteimportance = ("UPDATE notes "
                              "SET import = %s "
                              "WHERE note_id = %s")
        update_noteEventDate = ("UPDATE notes "
                                "SET date = %s "
                                "WHERE note_id = %s")
        update_noteTitle = ("UPDATE notes SET title = %s WHERE note_id = %s")
        add_note = ("INSERT INTO notes"
                        "(note_id, user_id, date_made, lastmod, notedata, date, import, title, color, repeating)"
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        add_usercon = ("INSERT INTO usercon"
                        "(user_id, note_id)"
                        "VALUES (%s, %s)")
        if note.getNew() == True:
            #if the note is new then add it to the database
            self.cursor.execute(add_note, (note.getId(), note.getOwner(), note.getDateMade(), note.getModified(), note.getText(), note.getEvent(), note.getImportance(), note.getTitle(), note.getColor(), note.getRepeating()))
            self.cursor.execute(add_usercon, (note.getOwner(), note.getId()))
        elif note.getMark() == True:
            #If the note has been marked for deletion then delete everything having to do with it in database
            ident = (note.getId(), )
            self.cursor.execute(delete_noteuser, ident)
            self.cursor.execute(delete_note, ident)
            self.cursor.execute(delete_notegroup, ident)
            self.cursor.execute(delete_notetag, ident)
        elif note.getUpdate() == True:
            #If note has been updated then update the database as well
            tags = note.getTags()
            oldtags = note.getOldTags()
            #Check if tags have been added
            for tag in tags:
                count = 0
                for oldtag in oldtags:
                    if tag == oldtag:
                        count += 1
                if count == 0:
                    self.cursor.execute(add_tag, tag[0], tag[1], note.getId())
            #Check if tags have been removed
            for oldtag in oldtags:
                count = 0
                for tag in tags:
                    if oldtag == tag:
                        count += 1
                if count == 0:
                    self.cursor.execute(remove_tag, oldtag[0], note.getId())
            #Check if new users are able to view the note
            for shareuser in note.getVisibility():
                count = 0
                for olduser in note.getOldVisibility():
                    if shareuser == olduser:
                        count += 1
                if count == 0:    
                    self.cursor.execute(add_usercon, shareuser, note.getId())
            #Check if users are no longer able to view the note
            for olduser in note.getOldVisibility():
                count = 0
                for shareuser in note.getVisibility():
                    if olduser == shareuser:
                        count += 1
                if count == 0:
                    conident = (note.getId(), olduser)
                    self.cursor.execute(delete_notecon, conident)
            self.cursor.execute(update_notedata, (note.getText(), note.getId()))
            self.cursor.execute(update_notedate, (note.getModified(), note.getId()))
            self.cursor.execute(update_notecolor,( note.getColor(), note.getId()))
            self.cursor.execute(update_noteimportance, (note.getImportance(), note.getId()))
            self.cursor.execute(update_noteEventDate, (note.getEvent(), note.getId()))
            self.cursor.execute(update_noteTitle, (note.getTitle(), note.getId()))
        
    def saveGroups(self, group):
        """Saves all data concerning groups to the database"""
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
        delete_groupnote=("DELETE FROM groupcon WHERE group_id = %s AND note_id = %s")
        delete_groupnotes=("DELETE FROM groupcon WHERE group_id = %s")
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
            #If the group is new add it to the database
            self.cursor.execute(new_group, (group.getId(), group.getName(), group.getDescription(), group.getOwner(), group.getPrivacy()))
            for member in group.getMembers():
                self.cursor.execute(add_groupmem, group.getId(), member)
        elif group.getMark() == True:
            #If the group is marked for deletion, delete everything related to the group from the database
            ident = (group.getId, )
            self.cursor.execute(delete_group, ident)
            self.cursor.execute(delete_groupmem, ident)
            self.cursor.execute(delete_groupnotes, ident)
        elif group.getUpdate() == True:
            #If the group is set to be updated then update the information related to it in the database
            self.cursor.execute(modify_desc, group.getDescription(), group.getId())
            self.cursor.execute(modify_name, group.getName(), group.getId())
            self.cursor.execute(modify_privacy, group.getPrivacy(), group.getId())
            oldmembers = group.getOldMembers()
            members = group.getMembers()
            #Check if new member have been added to the group
            for member in members:
                count = 0
                for oldmember in oldmembers:
                    if member == oldmember:
                        count += 1
                if count == 0:
                    self.cursor.execute(add_groupmem, group.getId(), member)
            #Check if members have been removed from the group
            for oldmember in oldmembers:
                count = 0
                for member in members:
                    if oldmember == member:
                        count += 1
                if count == 0:
                    memident = (oldmember, group.getId())
                    self.cursor.execute(remove_user, memident)
            
            notes = group.getNotes()
            oldnotes = group.getOldNotes()
            #Check if notes have been added to the group
            for note in notes:
                count = 0
                for oldnote in oldnotes:
                    if note == oldnote:
                        count += 1
                if count == 0:
                    self.cursor.execute(add_groupcon, group.getId(), note)
            #Check if notes have been removed from the group
            for oldnote in oldnotes:
                count = 0
                for note in notes:
                    if oldnote == note:
                        count += 1
                if count == 0:
                    noteident = (group.getId(), oldnote)
                    self.cursor.execute(delete_groupnote, noteident)               
            

class UserManager(object):

    def __init__(self):
        """Initializes UserManager object. Doesn't need any input, but setManagers() should be run before other functions."""
        self.userList = []
        self.currentUser = None
        self.nextId = 1

    def setManagers(self, _databaseManager, _groupManager, _noteManager, _guiManager):
        """Sets the manager attributes of UserManager object.
           The UserManager object must have its managers set after creation.. After all managers are made, setManagers should be called to finish initializing managers
           This is a utility function called in DatabaseManager.startup()

           _databaseManager DatabaseManager : The database controller object
           _groupManager    GroupManager    : The group controller object
           _noteManager     NoteManager     : The note controller object
           _guiManager      GUIManager      : The GUI controller object
        """
        self.databaseManager = _databaseManager
        self.userManager = _groupManager
        self.noteManager = _noteManager
        self.guiManager = _guiManager

    def login(self, username: str, password: str) -> bool:
        """Checks if username and password match a record, and logs in if successful

        username   str : Username to check records for
        password   str : Password to check match for

        Returns bool True if login is successful, and False if no record matches
        """
        for user in self.userList:
            if username == user.getUsername() and password == user.getPassword():
                self.currentUser = user
                return True
        return False

    def newUser(self, username, password):
        """Creates a new user entry. Automatically fills in the next available ID

        username str : Username to create new user with. Must be 16 characters or less.
        password str : Password to create new password with. Must be 16 characters or less.

        Returns newly created user object
        """
        user = self.addUser(self.nextId, username, password)
        user.setNew(True)
        return user

    def addUser(self, userId, username, password):
        """Inserts a user entry of the given ID to user list. 

        userId   int : primary ID of user. Must be a positive integer.
        password str : password of user. Must be 16 characters or less.
        username str : username of user. Must be 16 characters or less.

        returns User object
        """
        if(userId >= self.nextId):
            self.nextId = userId + 1
        newUser = User(userId, username, password)
        self.userList.append(newUser)
        return newUser

    def userJoinGroup(self, user, group):
        """Takes a user and a group and adds the user to the group. Returns None.

        user  User : user object to add to group
        group Group: group object to add user to

        returns None.
        """
        if group not in user.getGroups():
            user.addGroup(group)
        if user not in group.getMembers():
            group.addMember(group)

    def getCurrentUser(self):
        """Returns the current user attribute

        returns user object"""
        return self.currentUser

    def logout(self):
        self.currentUser = None

    def isUsernameTaken(self, username):
        for user in self.userList:
            if user.getUsername() == username:
                return True
        return False
            

class NoteManager(object):

    def __init__(self):
        self.noteList = []
        self.nextId = 1

    def setManagers(self, _databaseManager, _userManager, _groupManager, _guiManager):
        """This is a utility function called in DatabaseManager that links this controller to all the others.
           It must be called before using other functions.

           _databaseManager DatabaseManager : The database controller object
           _userManager     UserManager     : The user controller object
           _groupManager    GroupManager    : The group controller object
           _guiManager      GUIManager      : The GUI controller object
        """

        self.databaseManager = _databaseManager
        self.userManager = _userManager
        self.groupManager = _groupManager
        self.guiManager = _guiManager

    def addNote(self, noteId, owner, dateMade, lastModified, text, eventDate, importance, title, color, repeating):

        """Adds a note to the note list so it can be kept track of
        _noteId int
        owner str
        dateMade str
        lastModified str
        text str
        eventDate str
        important str
        title str
        color str
        repeating str
        """
        if noteId >= self.nextId:
            self.nextId = noteId + 1

        newNote = Note(noteId, owner, dateMade, lastModified, text, eventDate, importance, title, color, repeating)
        self.noteList.append(newNote)

    def generateNewNote(self):
        """ Creates a new, blank note

        returns Note object"""
        currentUser = self.userManager.getCurrentUser()
        ownerId = currentUser.getId()
        dateMade = datetime.datetime.now().strftime("%Y-%d-%m %H:%M:%S")
        
        newNote = Note(self.nextId, ownerId, dateMade, dateMade, "", None, 0, "", "none", False)
        newNote.setNew(True)
        self.nextId += 1
        self.noteList.append(newNote)
        return newNote
        

    def getNotes(self):
        """ This function gets a list of notes pertaining to the current user

        """
        userNotes = []
        currentUser = self.userManager.getCurrentUser()
        for note in self.noteList:
            if note.getOwner() == currentUser.getId() and note.getMark() == False:
                userNotes.append(note)
        userNotes.reverse()
        return userNotes


class GroupManager(object):
    def __init__(self):
        self.groupList = []
        self.nextId = 0
    def setManagers(self, _databaseManager, _userManager, _noteManager, _guiManager):
        """Because Managers have to be made all at once and reference each other, this function is called when this object is created on startup but after all managers are initalized"""
        self.databaseManager = _databaseManager
        self.userManager = _userManager
        self.noteManager = _noteManager
        self.guiManager = _guiManager
    def userJoinGroup(self, user, group):
        """Adds a user to a group"""
        self.userManager.userJoinGroup(user,group)
    def addGroup(self, groupId, groupname, description, owner, privacy):
        "Adds a group to the group list so it can be kept track of"
        if groupId >= self.nextId:
            self.nextId = groupId + 1
        newGroup = Group(groupId, groupname, description, owner, privacy)
        self.groupList.append(newGroup)
    def generateNewGroup(self):
        newGroup = Group(self.nextId, "", "", self.userManager.getCurrentUser().getId(), True)
        self.nextId += 1
        self.groupList.append(newGroup)
        newGroup.setNew(True)
        return newGroup

    def getJoinedGroups(self):
        currentUser = self.userManager.getCurrentUser()
        joinedGroups = []
        for group in self.groupList:
            if group.hasMember(currentUser):
                joinedGroups.append(group)
        return joinedGroups

    def getPublicGroups(self):
        joinedGroups = self.getJoinedGroups()
        publicGroups = []
        for group in self.groupList:
            if (not group.getPrivacy()) and (group not in joinedGroups):
                publicGroups.append(group)
        return publicGroups

    def isNameTaken(self, groupName):
        for group in self.groupList:
            if group.getName() == groupName:
                return True
        return False

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
        self.guiDict["twoPane"] = TwoPaneGUI(self.managerList, self.root)
        self.guiDict["calendar"] = CalendarGUI(self.managerList, self.root)
        self.guiDict["groups"] = GroupsGUI(self.managerList, self.root)

        self.openWindow("login")


        #If I had more time I would redesign this 
        self.groupDetails = GroupDetailsGUI(self.managerList, self.root)
        self.noteDetails = NoteDetailsGUI(self.managerList, self.root)

        self.root.mainloop()

    def openWindow(self, keyword):
        """Switches windows by hiding the current one and showing the requested"""
        oldWindow = self.currentWindow

        if keyword == "noteDetails":
            self.openNoteDetails()
            return
        if keyword == "groupDetails":
            self.openGroupDetails()
            return

        if(keyword in self.guiDict.keys()):
            self.currentWindow = self.guiDict[keyword]
            self.currentWindow.show()
        else:
            print("Incorrect keyword sent to guiManager.openWindow(keyword) . Incorrect keyword: \"" + keyword + "\" not found in guiDict")

        if oldWindow:
            oldWindow.hide()

        self.currentWindow.focus()
 
    def end(self):
        """Ends the tkinter program. Is called when x on any window is pressed"""
        self.root.destroy()

    def openGroupDetails(self):
        """Opens the GroupDetailGUI, grabbing appropriate information from group GUI"""
        currentGroup = self.currentWindow.getCurrentGroup()
        self.currentWindow.hide()
        self.currentWindow = self.groupDetails
        self.currentWindow.openGroupDetails(currentGroup)
        
        

    def openNoteDetails(self):
        """Opens the NoteDetailsGUI, grabbing appropriate information from previous GUI"""
        currentNote = self.currentWindow.getCurrentNote()
        self.currentWindow.hide()
        view = "twoPane" if self.currentWindow == self.guiDict["twoPane"] else "calendar"
        self.currentWindow = self.noteDetails
        self.noteDetails.openNoteDetails(currentNote, view)

    
    def popup(self, text):
        """Creates a simple popup with "ok" to close"""
        thePopup = PopupGUI(self.currentWindow, text)




#GUIs (view)




class AbstractGUI(object):
    """Parent class of all main GUI windows"""
    def __init__(self, managerList, parent):
        """
        managerList : List containing a UserManager, NoteManager, GroupManager, and GUIManager in that order
        parent : parent tkinter window
        """
        self.userManager = managerList[0]
        self.noteManager = managerList[1]
        self.groupManager = managerList[2]
        self.guiManager = managerList[3]
        self.databaseManager = managerList[4]
        self.window = Toplevel()
        self.window.withdraw()
        self.window.protocol("WM_DELETE_WINDOW",self.onClose)

    def show(self):
        """Makes window re-appear if invisible. Does nothing if visible. 
        Takes no input and returns None."""
        self.window.deiconify()

    def hide(self):
        """Makes window disppear if visible. Does not destroy window or data within it, just visually removes it from the screen. 
        Takes no input and returns None."""
        self.window.withdraw()

    def focus(self):
        """Forces focus onto the window."""
        self.window.focus_force()

    def onClose(self):
        """Closing any window using the system's red X will close the program. This is a helper function for the event handler set up in __init__ in order to do so.
        Takes no input and returns none"""
        self.guiManager.end()
        self.databaseManager.saveDatabase()

class PopupGUI(object):
    """Simple popup that is closed with an ok dialog"""
    def __init__(self, parent, message):
        self.window = Toplevel()
        self.window.geometry("200x125+100+100")
        messageLabel = Label(self.window, text=message)
        okButton = Button(self.window, text = "OK", command = self.closePopup)
        messageLabel.pack()
        okButton.pack()

        self.window.bind("<FocusOut>", self.closePopupEvent)
        self.window.focus_force()

    def closePopupEvent(self, event):
        self.closePopup()

    def closePopup(self):
        self.window.destroy()

class LoginGUI(AbstractGUI):
    def __init__(self, managerList, parent):
        """Creates the window and all its widgets."""
        super().__init__(managerList, parent)

        self.window.geometry("400x200+100+100")

        buttonFrame = Frame(master=self.window, height=150)
        buttonFrame.pack(fill=BOTH, side=BOTTOM, expand=True)

        entryFrame = Frame(master=self.window, height=250)
        entryFrame.pack(fill=BOTH, side=TOP, expand=True)

        registerButton = Button(buttonFrame, text = "Register", command = self.openRegisterWindow)
        registerButton.pack(side = LEFT, expand = True)
        loginButton = Button(buttonFrame, text = "Login", command = self.login)
        loginButton.pack( side = LEFT, expand = True)

        userNameFrame = Frame(entryFrame)
        userNameFrame.pack(expand = True)
        userNameLabel = Label(userNameFrame, text = "Username:")
        userNameLabel.pack(side=LEFT)
        self.userNameEntry = Entry(userNameFrame)
        self.userNameEntry.pack(side=RIGHT)

        passwordFrame = Frame(entryFrame)
        passwordFrame.pack(expand = True)
        passwordLabel = Label(passwordFrame, text = "Password:")
        passwordLabel.pack(side=LEFT)
        self.passwordEntry = Entry(passwordFrame)
        self.passwordEntry.pack(side=RIGHT)
         

    def openRegisterWindow(self):
        """Opens the register window, which will set loginGUI (this object) to invisible
        Takes no input and returns None"""
        self.guiManager.openWindow("register")

    def login(self):
        """Sends a login request to userManager. Logs user in and brings them to home if success, displays a popup if unsuccessful.
        Grabs username and password from entry fields.
        Takes no input and returns None"""
        userName = self.userNameEntry.get()
        password = self.passwordEntry.get()
        success = self.userManager.login(userName,password)
        if success:
            self.guiManager.openWindow("home")
        else:
            self.guiManager.popup("Incorrect Username and Password")

class RegisterGUI(AbstractGUI):
    def __init__(self, managerList, parent):
        super().__init__(managerList, parent)
        self.window.geometry("400x220+100+100")
        
        backButton = Button(self.window, text = "<-", command = self.backToLogin)
        backButton.pack(side = TOP, anchor = "nw")

        usernameLabel = Label(self.window, text = "Username:")
        passwordLabel = Label(self.window, text = "Password:")
        confirmPasswordLabel = Label(self.window, text = "Confirm Password:")
        registerButton = Button(self.window, text = "Register", command = self.newUser)

        self.usernameEntry = Entry(self.window)
        self.passwordEntry = Entry(self.window, show = "*")
        self.confirmPasswordEntry = Entry(self.window, show = "*")

        usernameLabel.pack()
        self.usernameEntry.pack()
        passwordLabel.pack()
        self.passwordEntry.pack()
        confirmPasswordLabel.pack()
        self.confirmPasswordEntry.pack()

        registerButton.pack()

    def newUser(self):
        """Runs when users click button labeled "Register". Creates a new user entry and reopens login window.
        Grabs username and password from entry fields
        Takes no input and returns none."""
        username = self.usernameEntry.get()
        password = self.passwordEntry.get()
        passwordConfirmation = self.confirmPasswordEntry.get()
        
        if len(username) > 16 or len(password) > 16:
            self.guiManager.popup("Username and password may only be up to 16 characters.")
            return
        if password != passwordConfirmation:
            self.guiManager.popup("Passwords do not match")
            return
        if self.userManager.isUsernameTaken(username):
            self.guiManager.popup("Username is already in use")
            return

        self.userManager.newUser(username, password)
        self.backToLogin()

    def backToLogin(self):
        """Hides this window and opens the login window.
        Takes no input and returns None"""
        self.guiManager.openWindow("login")

class HomeGUI(AbstractGUI):
    def __init__(self, managerList, parent):
        super().__init__(managerList, parent)
        self.window.geometry("450x250+100+100")

        backButton = Button(self.window, text = "<-", command = self.backToLogin)
        backButton.pack(side = TOP, anchor = "nw")

        self.twoPaneImage = PhotoImage(file="list.gif")
        #self.twoPaneImage = self.twoPaneImage.subsample(4)
        self.calendarImage = PhotoImage(file="calendar.gif")
        self.calendarImage = self.calendarImage.zoom(2)
        self.calendarImage = self.calendarImage.subsample(5)

        twoPaneViewButton = Button(self.window, image = self.twoPaneImage, command = self.openTwoPane)
        twoPaneViewButton.pack(side = LEFT, padx = (10,0))

        calendarViewButton = Button(self.window, image = self.calendarImage, command = self.openCalendar)
        calendarViewButton.pack(side = RIGHT, padx = (10,20))


    def openTwoPane(self):
        self.guiManager.openWindow("twoPane")

    def openCalendar(self):
        self.guiManager.openWindow("calendar")

    def backToLogin(self):
        self.guiManager.openWindow("login")


class CalendarGUI(AbstractGUI):
    """GUI class for the calendar view in VirtualPDA"""
    def __init__(self, managerList, parent):
        super().__init__(managerList,parent)
        self.window.geometry("800x600+100+100")
        self.today = datetime.datetime.now()
        self.firstDayOnCal = self.today
        self.currentMonth = self.today.month
        self.currentYear = self.today.year

        
        self.notesList = [] #Notes available to the user
        self.widgetNoteDict = {}
        self.dayFrames = [] # the 35 frames for all the days

        #This is gonna be a nightmare
        topFrame = Frame(self.window)
        bottomFrame = Frame(self.window)
        #Top Frame Stuff
        self.calendarLabel = Label(topFrame, text = self.today.strftime("%B '%y"), font=("TkDefaultFont", 24))
        self.twoPaneImage = PhotoImage(file="list.gif")
        self.twoPaneImage = self.twoPaneImage.subsample(4)
        twoPaneButton = Button(topFrame, image = self.twoPaneImage, command = self.switchToListView)
        backYearButton = Button(topFrame, text = "<<<", command = self.backYear)
        backMonthButton = Button(topFrame, text = "<",command = self.backMonth)
        forwardYearButton = Button(topFrame, text = ">>>", command = self.forwardYear)
        forwardMonthButton = Button(topFrame, text = ">", command = self.forwardMonth)

        twoPaneButton.pack(side = RIGHT, anchor = "ne")
        forwardYearButton.pack(side = RIGHT)
        forwardMonthButton.pack(side = RIGHT)
        backYearButton.pack(side = LEFT)
        backMonthButton.pack(side = LEFT)
        self.calendarLabel.pack()


        #Bottom Frame stuff

        self.calendarFrame = Frame(bottomFrame)

        topFrame.pack(side = TOP, fill = BOTH)
        bottomFrame.pack(side = BOTTOM, fill = BOTH, expand = True)
        self.calendarFrame.pack(side = RIGHT, fill = BOTH, expand = True)

        self.undatedColumn = Frame(bottomFrame)
        self.undatedColumn.pack(side = LEFT, fill = Y)

        for i in range(7):
            days = ["S","M","T","W","T","F","S"]
            dayLabel = Label(self.calendarFrame, text = days[i])
            dayLabel.place(y = 0, relx = i * 1/7 + 1/15)
            #dayLabel.grid(row = 0, column = i,)

        #menu
        self.menuBar = Menu(self.window)
        self.window["menu"] = self.menuBar

        userMenu = Menu(self.menuBar)
        self.menuBar.add_cascade(label = "User", menu = userMenu)
        userMenu.add_command(label = 'Logout', command = self.logout)
        userMenu.add_command(label = "Groups", command = self.openGroups)
        #self.menuBar.entryconfig("User", state = DISABLED)

    def logout(self):
        """Logs the user out and goes back to first window
            returns None"""
        self.userManager.logout()
        self.guiManager.openWindow("login")

    
    def updateCalendarFrame(self):
        self.widgetNoteDict = {}
        self.dayFrames = []

        for widg in self.calendarFrame.winfo_children():
            if str(type(widg)) == "<class 'tkinter.Frame'>":
                widg.destroy()

        day = datetime.datetime(self.currentYear, self.currentMonth, 1).replace(day = 1)
        while(day.strftime("%w") != "0"):
            day = day - datetime.timedelta(days = 1)
        self.firstDayOnCal = day


        for i in range(35):
            dayList = []
            dayFrame = self.createDayFrame(day, i)
            dayFrame.place(relwidth = 1/7, relheight = .19, relx = (i%7)*(1/7), rely = ((i//7) * 1/5) * .95 + .05)
            self.dayFrames.append(dayFrame)
            day = day + datetime.timedelta(days = 1)
        
    def newNote(self, event):
        note = self.noteManager.generateNewNote()
        dayOnCalIndex = self.dayFrames.index(event.widget)
        day = self.firstDayOnCal
        day = day + datetime.timedelta(days = dayOnCalIndex)
        newNoteLabel = Label(event.widget, text = "Untitled", bd = 1, relief = GROOVE)
        newNoteLabel.bind("<Button-1>", self.doubleClickNoteLabel)
        newNoteLabel.pack(side = TOP)
        self.widgetNoteDict[newNoteLabel] = note
        note.setEvent(day.strftime("%Y-%m-%d"))

        self.currentNote = note
        self.updateCalendarFrame()
        self.guiManager.openWindow("noteDetails")

        


    def createDayFrame(self, day, index):
        dayNumber = day.strftime("%d")
        dayText = day.strftime("%Y-%m-%d")
        dayFrame = Frame(self.calendarFrame, relief = RIDGE, bd = 2)
        dayFrame.bind("<Double-Button-1>", self.newNote)
        numberLabel = Label(dayFrame, text = dayNumber)
        numberLabel.pack(side = BOTTOM, anchor = "se")

        for note in self.notesList:
            if note.getEvent() == None:
                continue
            if dayText in note.getEvent():
                title = note.getTitle()
                if title == "":
                    title = "Untitled"
                noteLabel = Label(dayFrame, text = title, bd = 1, relief = GROOVE)
                noteColor = note.getColor()
                if noteColor == "red":
                    noteLabel["bg"] = "#FFAAAA"
                elif noteColor == "blue":
                    noteLabel["bg"] = "#AAAAFF"
                elif noteColor == "green":
                    noteLabel["bg"] = "#AAFFAA"
                elif noteColor == "yellow":
                    noteLabel["bg"] = "#FFFF99"
                elif noteColor == "purple":
                    noteLabel["bg"] = "#BB99FF"
                noteLabel.bind("<Double-Button-1>", self.doubleClickNoteLabel)
                noteLabel.pack(side = TOP)
                self.widgetNoteDict[noteLabel] = note
        return dayFrame


    def getCurrentNote(self):
        return self.currentNote

    def clickNoteLabel(self, event):
        #TODO
        return

    def doubleClickNoteLabel(self, event):
        labelClicked = event.widget
        self.currentNote = self.widgetNoteDict[labelClicked]
        self.guiManager.openWindow("noteDetails")

        return

    def openGroups(self):
        self.guiManager.openWindow("groups")

    def switchToListView(self):
        self.guiManager.openWindow("twoPane")

    def updateMonthLabel(self):
        self.calendarLabel["text"] = datetime.datetime(self.currentYear,self.currentMonth,1).strftime("%B '%y")
        

    def backYear(self):
        self.currentYear -= 1
        self.updateMonthLabel()
        self.updateCalendarFrame()

    def backMonth(self):
        self.currentMonth -= 1
        if self.currentMonth == 0:
            self.currentMonth = 12
            self.currentYear -= 1
        self.updateMonthLabel()
        self.updateCalendarFrame()

    def forwardYear(self):
        self.currentYear += 1
        self.updateMonthLabel()
        self.updateCalendarFrame()
    
    def forwardMonth(self):
        self.currentMonth += 1
        if self.currentMonth == 13:
            self.currentMonth = 1
            self.currentYear += 1
        self.updateMonthLabel()
        self.updateCalendarFrame()
        
        

    def show(self):
        """Makes window re-appear if invisible, and loads in Notes from current user into the GUI 
        Takes no input and returns None."""

        self.window.deiconify()
        self.notesList = self.noteManager.getNotes()
        self.updateCalendarFrame()
        

class TwoPaneGUI(AbstractGUI):
    """GUI Class for the Two Pane View / List View in VirtualPDA"""
    def __init__(self, managerList, parent):
        super().__init__(managerList,parent)
        self.window.geometry("800x600+100+100")
        self.notesList = []
        self.notesIndex = 0
        self.currentNote = None



        #outer frames
        leftFrame = Frame(self.window,  width = 400)
        leftFrame.pack_propagate(False)
        self.infoFrame = Frame(self.window,  width = 400)

        leftFrame.pack(side = LEFT, fill = BOTH)
        self.infoFrame.pack(side= RIGHT, fill = BOTH)
        
        #left widgets
        listControlsFrame = Frame(leftFrame)
        newNotesButton = Button(listControlsFrame, text = "+", command = self.newNote)
        scrollUpButton = Button(listControlsFrame, text = "^", command = self.scrollUp)
        scrollDownButton = Button(listControlsFrame,text= "v", command = self.scrollDown)
        self.notesFrame = Frame(leftFrame, bg = "red")

        self.notesFrame.pack(side = TOP, fill = BOTH)
        listControlsFrame.pack(side = BOTTOM, fill = X)
        scrollDownButton.pack(side = RIGHT)
        scrollUpButton.pack(side = RIGHT)
        newNotesButton.pack(side = LEFT, fill = X)

        #right widgets
        calendarViewFrame = Frame(self.infoFrame, width = 50, height = 50, bd = 3, relief = RAISED)
        calendarViewFrame.pack_propagate(True)
        calendarViewFrame.pack(side = TOP, anchor = "ne")

        self.calendarImage = PhotoImage(file = "calendar.gif")
        self.calendarImage = self.calendarImage.subsample(12)
        switchLabel = Label(calendarViewFrame, image = self.calendarImage)
        switchLabel.pack()
        switchLabel.bind("<Button-1>",self.openCalendarView)
        calendarViewFrame.bind("<Button-1>",self.openCalendarView)


        titleFrame = Frame(self.infoFrame, width = 400, height = 20)
        titleFrame.pack_propagate(False)
        tagFrame = Frame(self.infoFrame, width = 400, height = 20)
        tagFrame.pack_propagate(False)
        textBoxFrame = Frame(self.infoFrame, width = 400, height = 480)
        textBoxFrame.pack_propagate(False)
        self.saveButton = Button(self.infoFrame,text = "save", command = self.saveCurrentNote, state = DISABLED)
        self.deleteButton = Button(self.infoFrame,text = "delete", command = self.deleteCurrentNote, state = DISABLED)

        titleFrame.pack(side=TOP)
        tagFrame.pack(side=TOP)
        textBoxFrame.pack(side=TOP)
        self.saveButton.pack(side=BOTTOM, fill = X)
        self.deleteButton.pack(side=BOTTOM, anchor = "se")

        #right subwidgets

        titleLabel = Label(titleFrame, text = "Title:")
        self.titleEntry = Entry(titleFrame, state = DISABLED)
        titleLabel.pack(side = LEFT)
        self.titleEntry.pack(side = LEFT, fill = X, expand = True)

        self.detailsButton = Button(tagFrame, text = "details", command = self.openNoteDetails, state = DISABLED)
        tagsLabel = Label(tagFrame, text = "Tags:")
        self.tagsEntry = Entry(tagFrame, state = DISABLED)
        tagsLabel.pack(side = LEFT)
        self.tagsEntry.pack(side = LEFT, fill = X, expand = True)
        self.detailsButton.pack(side = RIGHT)

        self.textBox = Text(textBoxFrame, state = DISABLED)
        self.textBox.pack(fill = BOTH, expand = True)

    def deleteCurrentNote(self):
        self.currentNote.setMark()
        self.notesList.remove(self.currentNote)
        self.updateNotesList()
        self.selectNote(-1)
        return True


    def logout(self):
        """Logs the user out and goes back to first window
            returns None"""
        self.userManager.logout()
        self.guiManager.openWindow("login")
    
    def openCalendarView(self, event):
        self.saveCurrentNote()
        self.guiManager.openWindow("calendar")

    def openNoteDetails(self):
        """ Opens GUI with currently selected note's details
            returns None"""
        self.saveCurrentNote()
        self.guiManager.openWindow("noteDetails")

    def saveCurrentNote(self):
        """ Grabs info from widgets, saves note, and updates display
            returns False if successful (with popup) and True otherwise"""
        if len(self.titleEntry.get()) > 32:
            self.guiManager.popup("Title must be 32 characters or less")
            return False
        if self.currentNote == None:
            return False

        self.currentNote.setText(self.textBox.get("1.0", "end-1c"))
        self.currentNote.setTitle(self.titleEntry.get())
        self.currentNote.setTags(self.tagsEntry.get())#TODO tags


        self.currentNote.setUpdate(True)

        self.updateNotesList()
        return True
    def newNote(self):
        """ Creates a new note, inserts it to the top of the list, and automatically selects it
            returns None"""
        theNewNote = self.noteManager.generateNewNote()
        self.notesList.insert(0, theNewNote)
        self.notesIndex = 0
        self.updateNotesList()
        self.select0("")


    def createNoteFrame(self, parent, note, bindIndex):
        """ Creates a tkinter frame object with a note's specifications for use in the note list in TwoPaneGUI

            parent          : Valid tkinter parent object
            note       Note : Note object to grab data from
            bindIndex  int  : Index value 0 to 3 inclusive for mouse-click binding to help select notes.

            returns a Frame with decorators for title, content, color, and priority
        """

        noteTitle = note.getTitle()
        noteContent = note.getText()
        noteColor = note.getColor()
        noteImportance = note.getImportance()

        noteFrame = Frame(parent, bd = 2, relief = GROOVE, width = 400, height = 137)
        noteFrame.pack_propagate(False)
        importanceLabel = Label(noteFrame, text=("!" * noteImportance))
        color = ""
        if noteColor == "red":
            noteFrame["bg"] = "#FFAAAA"
        elif noteColor == "blue":
            noteFrame["bg"] = "#AAAAFF"
        elif noteColor == "green":
            noteFrame["bg"] = "#AAFFAA"
        elif noteColor == "yellow":
            noteFrame["bg"] = "#FFFF99"
        elif noteColor == "purple":
            noteFrame["bg"] = "#BB99FF"
        elif (bindIndex + self.notesIndex) %2 == 0:
            noteFrame["bg"] = "#F0F0F0"
        else:
            noteFrame["bg"] = "#E0E0E0"

        contentLabel = Label(noteFrame, text = noteContent)
        titleLabel = Label(noteFrame)
        if noteTitle == "":
            titleLabel["text"] = "Untitled"
        else:
            titleLabel["text"] = noteTitle

        if bindIndex == 0:
            command = self.select0
        elif bindIndex == 1:
            command = self.select1
        elif bindIndex == 2:
            command = self.select2
        elif bindIndex == 3:
            command = self.select3
        else:
            print("error in twoPaneGUI.createNoteFrame() incorrect bindIndex range 0<= x <=3")
        importanceLabel.bind("<Button-1>", command)
        contentLabel.bind("<Button-1>", command)
        titleLabel.bind("<Button-1>", command)
        noteFrame.bind("<Button-1>", command)

        importanceLabel.pack(side = RIGHT)
        titleLabel.pack(side = TOP)
        contentLabel.pack(side = BOTTOM)
        
        noteFrame.pack()

        return noteFrame

    def updateNotesList(self):
        """Updates note list in GUI. Used for scrolling and updating list.
        returns None"""
        for oldFrame in self.notesFrame.winfo_children():
            oldFrame.destroy()

        listMax = len(self.notesList)
        if listMax > self.notesIndex:
            note0 = self.createNoteFrame(self.notesFrame, self.notesList[self.notesIndex], 0)
        if listMax > self.notesIndex + 1:
            note1 = self.createNoteFrame(self.notesFrame, self.notesList[self.notesIndex+1], 1)
        if listMax > self.notesIndex + 2:
            note2 = self.createNoteFrame(self.notesFrame, self.notesList[self.notesIndex+2], 2)
        if listMax > self.notesIndex + 3:
            note3 = self.createNoteFrame(self.notesFrame, self.notesList[self.notesIndex+3], 3)

        self.window.update()

    def scrollDown(self):
        """ Scrolls the list of notes down"""
        if len(self.notesList) > self.notesIndex + 4:
            self.notesIndex += 1
            self.updateNotesList()

    def scrollUp(self):
        """ Scrolls the list of notes up"""
        if self.notesIndex > 0:
            self.notesIndex -= 1
            self.updateNotesList()
        
    def select0(self, event):
        """ Binding method for helping select notes on list (using frames instead of buttons)"""
        self.selectNote(0)

    def select1(self, event):
        """ Binding method for helping select notes on list (using frames instead of buttons)"""
        self.selectNote(1)

    def select2(self, event):
        """ Binding method for helping select notes on list (using frames instead of buttons)"""
        self.selectNote(2)

    def select3(self, event):
        """ Binding method for helping select notes on list (using frames instead of buttons)"""
        self.selectNote(3)

    def selectNote(self, index):
        """ Selects or deselects note from list

        index int : Index value of note to select. -1 for deselecting all.

        returns None"""
        if index == -1:
            self.currentNote = None
            for box in self.notesFrame.winfo_children():
                box.config(relief = GROOVE)
            self.textBox.delete("1.0", END)
            self.titleEntry.delete(0, END)
            self.tagsEntry.delete(0, END)
            self.tagsEntry["state"] = DISABLED
            self.titleEntry["state"] = DISABLED
            self.textBox["state"] = DISABLED
            self.saveButton["state"] = DISABLED
            self.deleteButton["state"] = DISABLED
            self.detailsButton["state"] = DISABLED
            self.window.update()
            return
        if self.currentNote is not None:
            if not self.saveCurrentNote():
                return

        for box in self.notesFrame.winfo_children():
            if(index == self.notesFrame.winfo_children().index(box)):
                box.config(relief = SUNKEN)
            else:
                box.config(relief = GROOVE)

        self.currentNote = self.notesList[self.notesIndex + index]
        #self.tagsEntry["state"] = NORMAL #TODO tags
        self.titleEntry["state"] = NORMAL
        self.textBox["state"] = NORMAL
        self.saveButton["state"] = NORMAL
        self.deleteButton["state"] = NORMAL
        self.detailsButton["state"] = NORMAL

        self.textBox.delete("1.0", END)
        self.textBox.insert("1.0", self.currentNote.getText())
        self.titleEntry.delete(0, END)
        self.titleEntry.insert(0, self.currentNote.getTitle())
        self.tagsEntry.delete(0, END)
        self.titleEntry.insert(0, self.currentNote.getTags())

        

    def show(self):
        """Makes window re-appear if invisible, and loads in Notes from current user into the GUI 
        Takes no input and returns None."""
        super().show()
        self.notesList = self.noteManager.getNotes()
        self.updateNotesList()
    
    def hide(self):
        """Makes window disappear if visible and deselects all notes"""
        super().hide()
        self.selectNote(-1)

    def getCurrentNote(self):   
        """Returns note currently being used by GUI"""
        return self.currentNote


class NoteDetailsGUI(AbstractGUI):
    """This GUI is used dually by both TwoPaneGUI and CalendarGUI in order to show the full details of a note object."""

    def __init__(self, managerList, parent):
        super().__init__(managerList,parent)
        self.window.geometry("400x700+100+100")
        self.backTo = ""
        self.currentNote = None

        #Top layer widgets top to bottom
        backButton = Button(self.window, text = "<- Save", command = self.back)
        titleFrame = Frame(self.window)
        tagFrame = Frame(self.window)
        contentLabel = Label(self.window, text = "Content:")
        self.contentBox = Text(self.window, height = 12)
        dateFrame = Frame(self.window)
        priorityFrame = Frame(self.window)
        colorFrame = Frame(self.window)
        sharedFrame = Frame(self.window)
        self.sharedList = Listbox(self.window)

        self.idText = StringVar()
        self.creatorText = StringVar()
        self.createdText = StringVar()

        idLabel = Label(self.window, textvariable = self.idText)
        creatorLabel = Label(self.window, textvariable = self.creatorText)
        createdLabel = Label(self.window, textvariable = self.createdText)

        backButton.pack(side = TOP, anchor = "nw")
        titleFrame.pack(side = TOP)
        tagFrame.pack(side = TOP)
        contentLabel.pack(side = TOP)
        self.contentBox.pack(side = TOP)
        dateFrame.pack(side = TOP)
        priorityFrame.pack(side = TOP)
        colorFrame.pack(side = TOP)
        sharedFrame.pack(side = TOP)
        self.sharedList.pack(side = TOP)
        idLabel.pack(side = TOP)
        creatorLabel.pack(side = TOP)
        createdLabel.pack(side = TOP)

        #Second layer widgets
        titleLabel = Label(titleFrame, text = "Title:")
        self.titleEntry = Entry(titleFrame)
        titleLabel.pack(side = LEFT)
        self.titleEntry.pack(side = RIGHT, fill = X)

        tagLabel = Label(tagFrame, text = "Tags:")
        self.tagEntry = Entry(tagFrame, state = DISABLED) #TODO enable
        tagLabel.pack(side = LEFT)
        self.tagEntry.pack(side = RIGHT, fill = X)

        dateLabel = Label(dateFrame, text= "Date (yyyy-mm-dd):")
        self.dateEntry = Entry(dateFrame)
        dateLabel.pack(side = LEFT)
        self.dateEntry.pack(side = RIGHT, fill = X)

        priorityLabel = Label(priorityFrame, text = "Priority:")
        self.priorityEntry = Scale(priorityFrame, orient = HORIZONTAL, from_ = 0, to = 4)
        priorityLabel.pack(side = LEFT)
        self.priorityEntry.pack(side = RIGHT, fill = X)

        colorLabel = Label(colorFrame, text = "Color:")
        self.colorValues = ("none", "red", "blue", "green", "purple", "yellow")
        self.colorEntry = ttk.Combobox(colorFrame, values = self.colorValues, state = "readonly")
        self.colorEntry.current(0)
        colorLabel.pack(side = LEFT)
        self.colorEntry.pack(side = RIGHT)

        sharedLabel = Label(sharedFrame, text = "Shared with:")
        #sharedButton = Button(sharedFrame, text = "Share", command = share())
        sharedLabel.pack(side = LEFT)
        #sharedButton.pack(side = RIGHT)

    def share():
        #TODO
        print("ERROR: NoteDetailsGUI.share() should not have run")
        return

    def openNoteDetails(self, note, view):
        """ This function is called by GUIManager in lieu of AbstractGUI.show() in order to load in note data and set
            whether calendar or two pane view should be returned too on close.

            note   Note : note object to load in
            view   str  : string either "calendar" or "TwoPane"
            
            returns None
        """
        self.backTo = view
        self.currentNote = note

        self.titleEntry.delete(0, END)
        self.titleEntry.insert(0, self.currentNote.getTitle())
        self.tagEntry.delete(0, END)
        self.tagEntry.insert(0, self.currentNote.getTags())
        self.contentBox.delete("1.0", END)
        self.contentBox.insert("1.0", self.currentNote.getText())
        self.dateEntry.delete(0, END)
        if(self.currentNote.getEvent() != None):
            self.dateEntry.insert(0, self.currentNote.getEvent())
        self.priorityEntry.set(self.currentNote.getImportance())
        self.colorEntry.current(self.colorValues.index(self.currentNote.getColor()))
        self.idText.set("Note ID:" + str(self.currentNote.getId()))
        self.creatorText.set("Creator ID:" + str(self.currentNote.getOwner()))
        self.createdText.set("Created :" + self.currentNote.getDateMade())
        self.show()


    def back(self):
        """Saves and goes back to previous window

        returns None"""
        if self.save():
            self.guiManager.openWindow(self.backTo)
        

    def save(self):
        """ Grabs data from widgets and saves to note

        returns True if successful and false Otherwise"""

        if len(self.titleEntry.get()) > 32:
            self.guiManager.popup("Title must be less than 32 characters")
            return False
        date = self.dateEntry.get()
        if date != "":
            if len(date) != 10:
                self.guiManager.popup("Date must be a valid date in yyyy-mm-dd format (or blank)")
                return False
            try:
                datetime.datetime.strptime(date,"%Y-%m-%d")
            except ValueError:
                self.guiManager.popup("Date must be a valid date in yyyy-mm-dd format (or blank)")
                return False
        self.currentNote.setUpdate(True)

        self.currentNote.setTitle(self.titleEntry.get())
        self.currentNote.setTags(self.tagEntry.get())
        self.currentNote.setText(self.contentBox.get("1.0","end-1c"))
        self.currentNote.setEvent(date)
        self.currentNote.setImportance(self.priorityEntry.get())
        self.currentNote.setColor(self.colorEntry.get())
        return True


class GroupsGUI(AbstractGUI):
    def __init__(self, managerList, parent):
        super().__init__(managerList,parent)
        
        self.userGroups = []
        self.publicGroups = []
        self.userList = []

        self.window.geometry("800x600+100+100")
        
        topBarFrame = Frame(self.window, height = 40, width = 800)
        mainFrame = Frame(self.window, height = 560, width = 800)

        topBarFrame.pack(side = TOP, fill = BOTH)
        mainFrame.pack(side = BOTTOM, fill = BOTH, expand = True)

        #topBarFrame
        newGroupButton = Button(topBarFrame, text = "New group", command = self.createNewGroup)
        backButton = Button(topBarFrame, text = "<--", command = self.backToHome)

        newGroupButton.pack(side = RIGHT)
        backButton.pack(side = LEFT)

        #0mainFrame
        leftFrame = Frame(mainFrame, width = 300)
        rightFrame = Frame(mainFrame, width = 500)

        leftFrame.pack(side = LEFT, fill = BOTH, expand = True)
        rightFrame.pack(side = RIGHT, fill = BOTH, expand = True)

        #0.0leftFrame
        self.myGroupsListbox = Listbox(leftFrame)
        self.publicGroupsListbox = Listbox(leftFrame)

        self.myGroupsListbox.bind("<<ListboxSelect>>", self.selectMyGroup)
        self.publicGroupsListbox.bind("<<ListboxSelect>>", self.selectPublicGroup)
        
        self.myGroupsListbox.pack(side = TOP, fill = BOTH, expand = True)
        self.publicGroupsListbox.pack(side = BOTTOM, fill = BOTH, expand = True)

        #0.1rightFrame
        self.titleLabel = Label(rightFrame, text = "grouptitle", font = ("TkDefaultFont", 30))
        groupInfoFrame = Frame(rightFrame)
        buttonFrame = Frame(rightFrame)

        self.titleLabel.pack(side = TOP)
        groupInfoFrame.pack(side = TOP, fill = BOTH, expand = TRUE)
        buttonFrame.pack(side = BOTTOM)

        #0.1.0groupInfoFrame
        groupDescriptionFrame = Frame(groupInfoFrame, width = 250)
        #groupDescriptionFrame.pack_propagate(False)
        groupMembersFrame = Frame(groupInfoFrame, width = 250)

        groupDescriptionFrame.pack(side = LEFT, fill = BOTH, expand = True)
        groupMembersFrame.pack(side = RIGHT, fill = BOTH, expand = True)

        #0.1.0.0groupDescriptionFrame
        descriptionLabel = Label(groupDescriptionFrame, text = "Description")
        self.descriptionTextbox = Text(groupDescriptionFrame, height = 1, width = 1, state = DISABLED)
        ownerButtonFrame = Frame(groupDescriptionFrame)
        self.editButton = Button(ownerButtonFrame, text = "Edit", state = DISABLED, command = self.editGroup)
        self.leaveButton = Button(ownerButtonFrame, text = "Leave", state = DISABLED, command = self.leaveGroup)

        descriptionLabel.pack(side = TOP)
        self.descriptionTextbox.pack(side = TOP, fill = BOTH, expand = True)
        ownerButtonFrame.pack(side = BOTTOM)
        self.editButton.pack(side = LEFT)
        self.leaveButton.pack(side = RIGHT)

        #0.1.0.1groupMembersFrame
        membersLabel = Label(groupMembersFrame, text = "Members")
        self.membersListbox = Listbox(groupMembersFrame)
        memberManagementFrame = Frame(groupMembersFrame)
        self.kickButton = Button(memberManagementFrame, text = "-", state = DISABLED, command = self.kickMember)
        self.inviteCombobox = ttk.Combobox(memberManagementFrame)
        self.inviteButton = Button(memberManagementFrame, text = "+", command = self.inviteMember, state = DISABLED)

        membersLabel.pack(side = TOP)
        self.membersListbox.pack(side = TOP, fill = BOTH, expand = True)
        memberManagementFrame.pack(side = BOTTOM)
        self.kickButton.pack(side = LEFT)
        self.inviteButton.pack(side = RIGHT)
        self.inviteCombobox.pack(side = RIGHT)

        #0.1.1buttonFrame
        self.joinButton = Button(buttonFrame, text = "Join", state = DISABLED, command = self.joinGroup)

        self.joinButton.pack(side = BOTTOM)

    def joinGroup(self):
        pass

    def inviteMember(self):
        pass

    def kickMember(self):
        pass

    def editGroup(self):
        self.guiManager.openWindow("groupDetails")

    def leaveGroup(self):
        pass

    def selectMyGroup(self, event):
        if len(self.myGroupsListbox.curselection()) == 0:
            return
        self.publicGroupsListbox.selection_clear(0, END)
        index = self.myGroupsListbox.curselection()[0]
        self.currentGroup = self.userGroups[index]
        self.updateGroupInfo()
    
    def selectPublicGroup(self, event):
        if len(self.publicGroupsListbox.curselection()) == 0:
            return
        self.myGroupsListbox.selection_clear(0, END)
        index = self.publicGroupsListbox.curselection()[0]
        self.currentGroup = self.publicGroups[index]
        self.updateGroupInfo()

    def getCurrentGroup(self):
        return self.currentGroup

    def show(self):
        super().show()
        self.updateGroupLists()

    def updateGroupInfo(self):
        if(self.userManager.getCurrentUser().getId() == self.currentGroup.getOwner()):
            nstate = NORMAL
        else:
            nstate = DISABLED

        self.kickButton["state"] = nstate
        self.editButton["state"] = nstate

        if(self.currentGroup.hasMember(self.userManager.getCurrentUser())):
            nstate = NORMAL
        else:
            nstate = DISABLED
        self.leaveButton["state"] = nstate
        self.inviteButton["state"] = nstate
        self.joinButton["state"] = DISABLED if nstate == NORMAL else NORMAL

        members = self.currentGroup.getMembers()
        self.membersListbox.delete(0, END)
        for i in range(len(members)):
            self.membersListbox.insert(0, members[i])

        self.descriptionTextbox["state"] = NORMAL
        self.descriptionTextbox.delete("1.0", END)
        self.descriptionTextbox.insert("1.0", self.currentGroup.getDescription())
        self.descriptionTextbox["state"] = DISABLED
        
        self.titleLabel["text"] = self.currentGroup.getName()


    def updateGroupLists(self):
        self.userGroups = self.groupManager.getJoinedGroups()
        self.publicGroups = self.groupManager.getPublicGroups()

        self.myGroupsListbox.delete(0, END)
        self.publicGroupsListbox.delete(0, END)

        for i in range(len(self.userGroups)):
            self.myGroupsListbox.insert(i, self.userGroups[i].getName())
        for i in range(len(self.publicGroups)):
            self.publicGroupsListbox.insert(i, self.publicGroups[i].getName())


    def createNewGroup(self):
        newGroup = self.groupManager.generateNewGroup()
        self.userGroups.append(newGroup)
        self.currentGroup = newGroup
        self.guiManager.openWindow("groupDetails")


    def backToHome(self):
        self.guiManager.openWindow("home")

class GroupDetailsGUI(AbstractGUI): 
    def __init__(self, managerList, parent):
        super().__init__(managerList,parent)
        self.currentGroup = None
        self.window.geometry("800x600+100+100")

        nameFrame = Frame(self.window)
        privacyFrame = Frame(self.window)
        descriptionFrame = Frame(self.window)
        saveButton = Button(self.window, text = "Save", command = self.saveAndBack)

        nameFrame.pack()
        privacyFrame.pack()
        descriptionFrame.pack()
        saveButton.pack()

        self.radioValue = IntVar()

        nameLabel = Label(nameFrame, text="Group name")
        self.nameEntry = Entry(nameFrame)
        privacyLabel = Label(privacyFrame, text = "Privacy")
        privacyRadioPrivate = Radiobutton(privacyFrame, text = "Private", variable = self.radioValue, value = 0)
        privacyRadioPublic = Radiobutton(privacyFrame, text = "Public", variable = self.radioValue, value = 1)
        descriptionLabel = Label(descriptionFrame, text = "Group description")
        self.descriptionText = Text(descriptionFrame)

        nameLabel.pack(side = LEFT)
        self.nameEntry.pack(side = RIGHT)
        privacyLabel.pack(side = LEFT)
        privacyRadioPrivate.pack(side = RIGHT)
        privacyRadioPublic.pack(side = RIGHT)
        descriptionLabel.pack(side = LEFT)
        self.descriptionText.pack(side = RIGHT)

    def saveAndBack(self):
        if self.save():
            self.guiManager.openWindow("groups")

    def save(self):
        name = self.nameEntry.get()
        isPublic = self.radioValue.get()
        description = self.descriptionText.get("1.0", "end-1c")
        if self.groupManager.isNameTaken(name):
            self.guiManager.popup("Group name is already in use")
            return False
        if len(name) > 30:
            self.guiManager.popup("Group name must be 30 characters or less")
            return False
        if len(description) > 180:
            self.guiManager.popup("Group description must be 180 Characters or less")
            return False
        isPrivate = not isPublic
        self.currentGroup.setPrivacy(isPrivate)
        self.currentGroup.setDescription(description)
        self.currentGroup.setName(name)
        return True

    def openGroupDetails(self, group):
        self.currentGroup = group
        self.nameEntry.delete(0, END)
        self.nameEntry.insert(0, self.currentGroup.getName())
        isPrivate = self.currentGroup.getPrivacy()
        if isPrivate:
            self.radioValue.set(0)
        else:
            self.radioValue.set(1)
        self.descriptionText.delete("1.0", END)
        self.descriptionText.insert("1.0", self.currentGroup.getDescription())
        super().show()



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
        
    def getUpdate(self) -> bool:
        """Returns whether the object needs to be updated in the database or not"""
        return self.update
        
    def getMark(self) -> bool:
        """Returns whether the object needs to be deleted in the database or not"""
        return self.mark
        
    def getNew(self) -> bool:
        """Returns whether the object needs to have a new entry made for it in the database"""
        return self.new
    
    def setId(self, nId: int):
        """Changes the id value"""
        self.id = nId
    
    def setUpdate(self, change: bool):
        """Changes the update value"""
        self.update = change
        
    def setMark(self):
        """Changes the mark value to true since user has to go through a confirmation process before they want something deleted"""
        self.mark = True
        
    def setNew(self, change: bool):
        """Changes the new value"""
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
        self.oldTags = []
        self.visibleBy = []
        self.oldVisibility = []

    def edit(self, entertext: str):
        """Currently only allows adding to text, will eventually allow for full editing of text"""
        self.text = entertext
        
    def share(self, shareuser: int):
        """share note with other users"""
        self.visibleBy.append(shareuser)
        
    def addTag(self, newtag):
        """Adds a tag to the note"""
        count = 0
        for tag in self.tags:
            if tag == newtag:
                count += 1
        if count == 0:
            self.tags.append(newtag)
            
    def fillOldTags(self):
        """Fill the old tag list for when saving occurs"""
        for tag in self.tags:
            self.oldTags.append(tag)
            
    def fillOldUsers(self):
        """Fill the old user list for when saving occurs"""
        for user in self.visibleBy:
            self.oldVisibility.append(user)
            
    def getOldVisibility(self):
        """Return the list of old users that can see the note"""
        return self.oldVisibility
    
    def getOldTags(self):
        """Return the list of old tags that are on the note"""
        return self.oldTags
        
    def getOwner(self):
        """Return the owner of the note"""
        return self.owner
    
    def getDateMade(self):
        """Return the date the note was made"""
        return self.dateMade
    
    def getModified(self):
        """Return the date the note was last modified"""
        return self.lastModified
    
    def getText(self):
        """Return the text of the note"""
        return self.text
    
    def getEvent(self):
        """Return the date of the event if there is one"""
        return self.eventDate
    
    def getImportance(self):
        """Return the importance value of the note if there is one"""
        return self.importance
    
    def getTitle(self):
        """Return the title of the note if there is one"""
        return self.title
    
    def getColor(self):
        """Return the color of the note if there is one"""
        return self.color
    
    def getRepeating(self):
        """Return if the note event repeats or not"""
        return self.repeating
    
    def getTags(self):
        """Return the list of tags on the note"""
        return self.tags
    
    def getVisibility(self):
        """Return the list of people who can see the note"""
        return self.visibleBy
    
    def setOwner(self, nOwner):
        """Change the owner"""
        self.owner = nOwner
    
    def setModified(self, nModified):
        """Updates the date the note was modified on"""
        self.lastModified = nModified

    def setText(self, nText):
        """Updates the text content of the note"""
        self.text = nText
    
    def setEvent(self, nEvent):
        """Set the date of the event"""
        if(nEvent == ""):
            self.eventDate = None
            return
        self.eventDate = nEvent
    
    def setImportance(self, nImportance):
        """Set the importance value of the note"""
        self.importance = nImportance
    
    def setTitle(self, nTitle):
        """Set the title of the note"""
        self.title = nTitle
    
    def setColor(self, nColor):
        """Set the color of the note"""
        self.color = nColor
    
    def setRepeating(self, nRepeating):
        """Set if the note event is repeating or not"""
        self.repeating = nRepeating
    
    def setTags(self, nTags):
        """Set the tags list"""
        self.tags = nTags
    
    def setVisibility(self, nVisibility):
        """Set the list of users who can see the note"""
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
        """Returns the password"""
        return self.password
    
    def setGroups(self, nGroups):
        """Sets the list of groups"""
        self.groups = nGroups

    def setNotes(self, nNotes):
        """Sets the list of notes"""
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
    def __init__(self, _id, _groupname, _desc, _own, _privacy):
        """Precondition: _id is not 0. _owner is not 0
        Postcondition: Group object is initialized"""
        super().__init__(_id)
        self.name = _groupname
        self.description = _desc
        self.owner = _own
        self.isPrivate = _privacy
        self.members = [_own]
        self.oldMembers = []
        self.notes = []
        self.oldNotes = []
        
    def addUser(self, newuser):
        """Adds a user to the list of users in the group"""
        self.members.append(newuser)
        
    def setDescription(self, newdesc):
        """Edits the description of the group"""
        self.description = newdesc

    def hasMember(self, user):
        if user.getId() in self.members:
            return True
        return False

        
    def remUser(self, memind):
        """Removes a user from the group"""
        self.members.remove(memind)
        
    def setName(self, newname):
        """Edits the name of the group"""
        self.name = newname
        
    def fillOldMembers(self):
        """Fills the Old Members list for when saving occurs"""
        for member in self.members:
            self.oldMembers.append(member)
        
    def togglePrivacy(self):
        """Change the privacy setting of the group"""
        if (self.isPrivate == True):
            self.isPrivate == False
        else:
            self.isPrivate == True

    def setPrivacy(self, private):
        self.isPrivate = private
            
    def addNote(self, note):
        """Adds notes to the group note list"""
        self.notes.append(note)
        
    def fillOldNotes(self):
        """Fills the Old Notes list for when saving occurs"""
        for note in self.notes:
            self.oldNotes.append(note)
            
    def getOldNotes(self):
        """Return the list of old notes"""
        return self.oldNotes
    
    def getOldMembers(self):
        """Return the list of old members"""
        return self.oldMembers
            
    def getName(self):
        """Return the name of the group"""
        return self.name
    
    def getDescription(self):
        """Return the description of the group"""
        return self.description
    
    def getOwner(self):
        """Return the owner of the group"""
        return self.owner
    
    def getPrivacy(self):
        """Return the privacy of the group"""
        return self.isPrivate
    
    def getMembers(self):
        """Return the list of members of the group"""
        return self.members
    
    def setOwner(self, nOwner):
        """Changes the owner of the group"""
        self.owner = nOwner
    
    def setMembers(self, nMembers):
        """Changes the member list of the group"""
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
