# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 19:15:31 2021

@author: Justin
"""
import mysql.connector as mysql
import keyring
import getpass

#MySql Login
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
        database = mysql.connect(
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

#Database
cursor = database.cursor(buffered=True)
cursor.execute("DROP DATABASE {};".format(serviceId))