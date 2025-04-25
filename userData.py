import sqlite3

# c.execute("""CREATE TABLE UserData (
#     Name TEXT REQUIRED,
#     Email TEXT REQUIRED,
#     Password TEXT REQUIRED
#           )""")

def getData(Email):
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("SELECT * FROM UserData WHERE Email = ?", (Email,))
    data = c.fetchone()
    conn.close()
    return data

def insertData(Name, Email, Password):
    conn = sqlite3.connect('userData.db')
    c = conn.cursor()
    c.execute("INSERT INTO UserData (Name, Email, Password) VALUES (?, ?, ?)", (Name, Email, Password))
    conn.commit()
    conn.close()
    
    
    