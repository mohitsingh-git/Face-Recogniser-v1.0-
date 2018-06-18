import sqlite3 as lite
import os
con = lite.connect('User_Data.db')
with con:
    cur = con.cursor()
    cur.execute("DELETE FROM Users")
    name = ("%s" % cur.fetchone())

for root, dirs, files in os.walk('C:/Users/Mohit/Desktop/Kivy/src/dataset'):
    for f in files:
        os.unlink(os.path.join(root, f))

print("Done")