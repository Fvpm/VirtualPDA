from Classes.py import *

#Startup sequence

#1. Create Database Manager. __init__ will initialize connection to database
dbManager = DatabaseManager()
#2. Use Database Manager to load in data for User, Group, and Note Managers, which are created in and returned from database manager.
managerList = dbManager.startUp()
userManager = managerList[0]
noteManager = managerList[1]
groupManager = managerList[2]
guiManager = managerList[3]
#4. Open login window


