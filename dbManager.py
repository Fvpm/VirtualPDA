"""This file is just for testing keyring and creating the database separately from the other code"""

import mysql.connector as mysql
import keyring
import getpass

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


databaseManager = DatabaseManager()
