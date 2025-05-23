import sqlite3

# c.execute("""CREATE TABLE UserData (
#     Name TEXT REQUIRED,
#     Email TEXT REQUIRED,
#     Password TEXT REQUIRED
#     IsLoggedIn INTEGER DEFAULT 0,
#     Code INTEGER,
#     Profile_Pic BLOB,
#           )""")
# c.execute("PRAGMA foreign_keys = ON")
# c.execute("""CREATE TABLE Journals (
#                 Email TEXT REQUIRED,
#                 Journal_Body TEXT,
#                 Journal_Title TEXT,
#                 Travel_Pic BLOB,
#                 Country TEXT,
#                 City TEXT,
#                 District TEXT,
#                 Latitude REAL,
#                 Longitude REAL,
#                 FOREIGN KEY (Email) REFERENCES UserData(Email)
#           )""")





def getData(Email):
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("SELECT rowid,* FROM UserData WHERE Email = ?", (Email,))
    data = c.fetchone()
    conn.close()
    return data if data else None

def insertData(Name, Email, Password):
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("INSERT INTO UserData (Name, Email, Password) VALUES (?, ?, ?)", (Name, Email, Password))
    conn.commit()
    conn.close()

def insertJournal(Email, Journal_Body, Journal_Title, Travel_Pic, Country, City, District, Latitude, Longitude):
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("INSERT INTO Journals (Email, Journal_Body, Journal_Title, Travel_Pic, Country, City, District, Latitude, Longitude) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (Email, Journal_Body, Journal_Title, Travel_Pic, Country, City, District, Latitude, Longitude))
    conn.commit()
    conn.close()

def getJournals(Email):
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("SELECT rowid,* FROM Journals WHERE Email = ?", (Email,))
    data = c.fetchall()
    conn.close()
    return data if data else None

def changePassword(Email, Password):
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("UPDATE UserData SET Password = ? WHERE Email = ?", (Password, Email))
    conn.commit()
    conn.close()
    
def editJournal(rowid, email, journal_body, journal_title, travel_pic, country, city, district, latitude, longitude):
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("UPDATE Journals SET Journal_Body = ?, Journal_Title = ?, Travel_Pic = ?, Country = ?, City = ?, District = ?, Latitude = ?, Longitude = ? WHERE rowid = ? AND Email = ?",(journal_body, journal_title, travel_pic, country, city, district, latitude, longitude, rowid, email))
    conn.commit()
    conn.close()

def deleteJournal(rowid, email):
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("DELETE FROM Journals WHERE rowid = ? AND Email = ?", (rowid, email))
    conn.commit()
    conn.close()

def deleteUser(email):
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("DELETE FROM UserData WHERE Email = ?", (email,))
    c.execute("DELETE FROM Journals WHERE Email = ?", (email,))
    conn.commit()
    conn.close()

def getUserData(email):
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("SELECT rowid,* FROM UserData WHERE Email = ?", (email,))
    data = c.fetchone()
    conn.close()
    return data if data else None

def setCode(email, code):
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("UPDATE UserData SET Code = ? WHERE Email = ?", (code, email))
    conn.commit()
    conn.close()

def getCode(email):
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("SELECT Code FROM UserData WHERE Email = ?", (email,))
    data = c.fetchone()
    conn.close()
    return data[0] if data else None


def updateUserData(email, name):
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("UPDATE UserData SET Name = ? WHERE Email = ?", (name, email))
    conn.commit()
    conn.close()

def updateProfilePic(email, profile_pic):
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("UPDATE UserData SET Profile_Pic = ? WHERE Email = ?", (profile_pic, email))
    conn.commit()
    conn.close()

def showAllJournals():
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("SELECT rowid,* FROM Journals")
    data = c.fetchall()
    conn.close()
    return data if data else None

def showAllUsers():
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("SELECT rowid,* FROM UserData")
    data = c.fetchall()
    conn.close()
    return data if data else None

insertData("Arby", "arbyabani12@gmail.com", "1234byby")
# setCode("arby@gmail.com", 1234)
# print(getCode("arby@gmail.com")[0])
# print(showAllJournals())
print(showAllUsers())