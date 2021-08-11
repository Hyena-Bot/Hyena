import json

import psycopg2

conn = psycopg2.connect(
    dbname="hyena", user="postgres", host="localhost", password="22#December@2020"
)

cur = conn.cursor()

with open("./data.json", "r") as f:
    rows = json.loads(f.read())

for row in rows:

    print(row[0], row[1])
    cur.execute(
        "INSERT INTO prefixes(guild_id, prefix) VALUES(%s, %s)", (row[0], row[1])
    )

conn.commit()
cur.close()
conn.close()
