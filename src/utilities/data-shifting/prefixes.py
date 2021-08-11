import ast
import json

import psycopg2

conn = psycopg2.connect(
    "dbname='hyena' user='postgres' host='localhost' password='22#December@2020'"
)
cur = conn.cursor()
cur.execute("""SELECT * from prefixes""")
rows = cur.fetchall()
rows = [list(row) for row in rows]

for idx, row in enumerate(rows):
    row = list(row)
    rows[idx][1] = ast.literal_eval(row[1])

print(len(rows))

# json_formatted_str = json.dumps(rows, indent=4)

# with open('./data.json', 'w') as f:
#     f.write(json_formatted_str)
