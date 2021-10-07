"""
Currently coded for Python only, not coded to work with database

"""

from tkinter import *

#Managers

class UserManager(object):
    pass

class DatabaseManager(object):
    pass

class GroupManager(object):
    pass

class NoteManager(object):
    pass

class GUIManager(object):
    def __init__(self):
        self.currentWindow = ""
    def setManagers(self, userManager, databaseManager)
        pass

#GUIs

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
        
def main():
    user1 = User("Jason", "x1pho3nc0rp")
    user2 = User("Kylie", "t3n3m4n")
    note1 = Note(user1, user1, "0", "0", "", "0", 3, "Alexander Fails", "Red", False, "Junk")
    group1 = Group("Alexander Fan Club", "For people who love Alexander the Great", user1)
    
    print(user1.checkPass("x1pho3nc0rp"))
    user1.changePass("sh4d0wKn1gh7")
    user1.changeUser("Alex")
    print(user1.password)
    print(user1.username)
    user1.joinGroup(group1)
    print(user1.groups)
    user1.leaveGroup(group1)
    print(user1.groups)
    #print(user1.notes)
    #user1.createNote("0", "Behold the Empire")
    #print(user1.notes)
    user1.createGroup("Titanic", "For those who love Titanic")
    user1.joinGroup(group1)
    print(user1.groups)
    group1.addUser(user2)
    print(group1.members)
    group1.remUser(user1)
    print(group1.members)
    group1.editName("Rolling")
    group1.editDesc("For those who want to roll dice")
    print(group1.description)
    print(group1.name)
    print(group1.isPrivate)
    group1.togglePrivacy()
    print(group1.isPrivate)
    print(note1.vis)
    note1.share(user2)
    print(note1.vis)
    note1.edit("The cake is a lie")
    print(note1.text)
    

main()
