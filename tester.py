import mysql.connector as my
import hashlib

# Connect to MySQL database
pwrd = "krish113838G"


try:
    mycon = my.connect(host='localhost',
                       user='root',
                       password=pwrd)

except:
    print("Wrong password!")
    exit(0)

if not mycon.is_connected():
    print("Not able to connect to the server at this movement")
    exit(0)
    
else:
    print("Connected")

cr = mycon.cursor()
cr.execute("CREATE DATABASE IF NOT EXISTS AIVersus")
cr.execute("USE AIVersus")

password = input("password: ")
if password.isspace():
    exit(0)

elif len(password) < 8:
    exit(0)
    
elif not password.isalnum():
    exit(0)
    


emailId = input("email: ")
name = input("name: ")



cr.execute("CREATE TABLE IF NOT EXISTS user (name VARCHAR(100), email VARCHAR(50), password VARCHAR(50))")
# Use parameterized query to insert data
query = "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)"
values = (name, emailId, password)
cr.execute(query, values)




# Commit the transaction to save changes
mycon.commit()

print("User registered successfully!")

# Close the cursor and connection
cr.close()
mycon.close()

