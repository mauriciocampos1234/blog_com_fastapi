import sqlite3
conn = sqlite3.connect("app.db")
tables = [r[0] for r in conn.execute("select name from sqlite_master where type='table' order by name")]
print(tables)
