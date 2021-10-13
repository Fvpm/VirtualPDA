"""
Currently coded for Python only, not coded to work with database

"""

import mysql.connector
import datetime

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
        """Currently only allows adding to text, will eventually allow for full editing of text. expected input is string"""
        update_notedata = ("UPDATE notes"
                        "SET notedata = %s"
                        "WHERE note_id = %s")
        update_notedate = ("UPDATE notes"
                        "SET lastmod = %s"
                        "WHERE note_id = %s")
        cursor.execute(update_notedata, entertext, self.id)
        cursor.execute(update_notedate, datetime.now().date(), self.id)
        
    def addTag(self, newtag, tagtext):
        """Adds a new tag to the list of tags for the note. Expected inputs are int and string"""
        self.tags.append([newtag, tagtext])
        add_tag = ("INSERT INTO tags"
                        "(tag_id, tag_text, note_id)"
                        "VALUES (%(tag_id)s, %(tag_text)s, %(note_id)s)")
        cursor.execute(add_tag, newtag, tagtext, self.id)
        
    def removeTag(self, oldtag):
        """Removes a tag from the list of tags. Expected inputs are list"""
        self.tags.remove(oldtag)
        remove_tag = ("DELETE FROM tags WHERE tag_id = %s AND note_id = %s")
        cursor.execute(remove_tag, oldtag[0], self.id)
        
    def delete(self):
        """delete the note"""
        delete_note = ("DELETE FROM notes WHERE note_id = %s")
        delete_notegroup=("DELETE FROM groupcon WHERE note_id = %s")
        delete_noteuser=("DELETE FROM usercon WHERE note_id = %s")
        delete_notetag=("DELETE FROM tags WHERE note_id = %s")
        cursor.execute(delete_note, self.id)
        cursor.execute(delete_notegroup, self.id)
        cursor.execute(delete_noteuser, self.id)
        cursor.execute(delete_notetag, self.id)
        
    def share(self, shareuser):
        """share note with other users. expected input is int"""
        self.vis.append(shareuser)
        add_usercon = ("INSERT INTO usercon"
                        "(user_id, note_id)"
                        "VALUES (%(user_id)s, %(note_id)s)")
        cursor.execute(add_usercon, shareuser, self.id)
        
class User(DataObjects):
    def __init__(self, intuse, intpass):
        self.username = intuse
        self.password = intpass
        self.groups = []
        self.notes = []
        
    def changePass(self, newpassword):
        """allows user to change their password. must be logged in before they can change password. expected input is string"""
        self.password = newpassword
        modify_pass = ("UPDATE users"
                       "SET password = %s"
                       "WHERE user_id = %s")
        cursor.execute(modify_pass, newpassword, self.id)
        
    def checkPass(self, attempt):
        """checks users entered password and makes sure it matches their saved password. expected input is string"""
        if attempt == self.password:
            return True
        else:
            return False
        
    def createNote(self, date, entry):
        """create a new note. expected inputs are strings"""
        newnote=Note(self.id, self, date, date, entry, "", 0, "", "", False, "")
        self.notes.append(newnote)
        add_note = ("INSERT INTO notes"
                        "(note_id, user_id, date_made, lastmod, notedata, date, import, title, color, repeat)"
                        "VALUES (%(note_id)s, %(user_id)s, %(date_made)s, %(lastmod)s, %(notedata)s, %(date)s, %(import)s, %(title)s, %(color)s, %(repeat)s)")
        add_usercon = ("INSERT INTO usercon"
                        "(user_id, note_id)"
                        "VALUES (%(user_id)s, %(note_id)s)")
        cursor.execute(add_note, noteid, self.id, date, date, entry, "", 5, "", "", False)
        cursor.execute(add_usercon, self.id, noteid)
        
    def changeUser(self, newusername):
        """allows user to change their username. must be logged in before they can change username. expected input is string"""
        self.username = newusername
        modify_user = ("UPDATE users"
                       "SET username = %s"
                       "WHERE user_id = %s")
        cursor.execute(modify_user, newusername, self.id)
        
    def joinGroup(self, group):
        """Join a group. expected input is int"""
        self.groups.append(group)
        add_groupmem = ("INSERT INTO groupmem"
                        "(group_id, user_id)"
                        "VALUES (%(group_id)s, %(user_id)s)")
        cursor.execute(add_groupmem, group, self.id)
        
    def createGroup(self, groupname, desc, groupid, noteid):
        """Create a new group. expected inputs are strings"""
        newgroup = Group(groupname, desc, self)
        self.groups.append(newgroup)
        new_group = ("INSERT INTO groups"
                     "(group_id, name, description, user_id, privacy)"
                     "VALUES (%(group_id)s, %(name)s, %(description)s, %(user_id)s, %(privacy)s)")
        add_groupmem = ("INSERT INTO groupmem"
                        "(group_id, user_id)"
                        "VALUES (%(group_id)s, %(user_id)s)")
        add_groupcon = ("INSERT INTO groupcon"
                        "(group_id, note_id)"
                        "VALUES (%(group_id)s, %(note_id)s)")
        cursor.execute(new_group, groupid, groupname, desc, self.id, True)
        cursor.execute(add_groupmem, groupid, self.id)
        cursor.execute(add_groupcon, groupid, noteid)
        
    def leaveGroup(self, groupid):
        """removes user from a group voluntarily. expected input is int"""
        self.groups.remove(groupid)
        remove_self=("DELETE FROM groupmem WHERE user_id = %s")
        cursor.execute(remove_self, self.id)
        
    def delete(self):
        """delete the user"""
        delete_user = ("DELETE FROM users WHERE user_id = %s")
        delete_usergroup=("DELETE FROM groupmem WHERE user_id = %s")
        delete_usernote=("DELETE FROM usercon WHERE user_id = %s")
        delete_usergrouping=("DELETE FROM groups WHERE user_id = %s")
        delete_usernotes=("DELETE FROM notes WHERE user_id = %s")
        cursor.execute(delete_user, self.id)
        cursor.execute(delete_usergroup, self.id)
        cursor.execute(delete_usernote, self.id)
        cursor.execute(delete_usergrouping, self.id)
        cursor.execute(delete_usernotes)
    
class Group(DataObjects):
    def __init__(self, groupname, desc, own):
        self.name = groupname
        self.description = desc
        self.owner = own
        self.isPrivate = True
        self.members = [own]
        
    def addUser(self, newuser):
        """add a new user to the group. expected input is int"""
        self.members.append(newuser)
        add_groupmem = ("INSERT INTO groupmem"
                        "(group_id, user_id)"
                        "VALUES (%(group_id)s, %(user_id)s)")
        cursor.execute(add_groupmem, self.id, newuser)
        
    def editDesc(self, newdesc):
        """edit the description of the group. expected input is string"""
        self.description = newdesc
        modify_desc = ("UPDATE groups"
                       "SET description = %s"
                       "WHERE group_id = %s")
        cursor.execute(modify_desc, newdesc, self.id)
        
    def remUser(self, memind):
        """remove a user from the group. expected input is int"""
        self.members.remove(memind)
        remove_user=("DELETE FROM groupmem WHERE user_id = %s")
        cursor.execute(remove_user, memind)
        
    def editName(self, newname):
        """edit the name of the group. expected input is string"""
        self.name = newname
        modify_name = ("UPDATE groups"
                       "SET name = %s"
                       "WHERE group_id = %s")
        cursor.execute(modify_name, newname, self.id)
        
    def togglePrivacy(self):
        """Change the privacy setting of the group"""
        if (self.isPrivate == True):
            self.isPrivate == False
        else:
            self.isPrivate == True
        modify_privacy = ("UPDATE groups"
                       "SET privacy = %s"
                       "WHERE group_id = %s")
        cursor.execute(modify_privacy, self.isPrivate, self.id)
        
    def delete(self):
        """Delete the group"""
        delete_group = ("DELETE FROM groups WHERE group_id = %s")
        delete_groupmem=("DELETE FROM groupmem WHERE group_id = %s")
        delete_groupnote=("DELETE FROM groupcon WHERE group_id = %s")
        cursor.execute(delete_group, self.id)
        cursor.execute(delete_groupmem, self.id)
        cursor.execute(delete_groupnote, self.id)