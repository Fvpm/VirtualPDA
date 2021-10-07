from Classes import *

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
