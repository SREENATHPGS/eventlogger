import sqlite3

connection = sqlite3.connect('log_database.db')


with open('./log_db.sql') as f:
    connection.executescript(f.read())

# cur = connection.cursor()
# cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
#             ('First Post', 'Content for the first post')
#             )

connection.commit()
connection.close()