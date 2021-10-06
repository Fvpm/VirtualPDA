"""
Currently coded for Python only, not coded to work with database

"""

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
        self.groups.append(group.id)
        
    def createGroup(self, groupname, desc):
        """Create a new group"""
        newgroup = Group(groupname, desc, self)
        self.group.append(newgroup)
        
    def leaveGroup(self, groupid):
        self.group.remove(groupid)
        
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