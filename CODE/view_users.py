import sqlite3

# Connect to the database
conn = sqlite3.connect('users.db')  # Your database name

# Create a cursor
cursor = conn.cursor()

# Fetch data from 'user' table
cursor.execute("SELECT * FROM user")

# Fetch all rows
rows = cursor.fetchall()

# Print each row
for row in rows:
    print(row)

# Close the connection
conn.close()


