import psycopg2 as ps
from datetime import datetime
import uuid


# Connect to MySQL database
pwrd = "krish113838G"

try:
    mycon = ps.connect(
        host='localhost',
        user='postgres',
        password=pwrd,
        dbname = 'aiversus'
    )
    print("Connected")


except ps.Error as e:
    print(f"Database connection failed: {e}")
    exit(1)

cr = mycon.cursor()

def genUUID():
    while True:
        generated_uuid = str(uuid.uuid4())
        cr.execute('SELECT COUNT(*) FROM "chat_history" WHERE id = %s', (generated_uuid,))
        result = cr.fetchone()
        if result is not None and result[0] == 0:
            return generated_uuid




def insert_one(doc):
    # print(type(doc))
    
    # print(doc)
    if type(doc) != dict:
        print("Error: doc type is not Dict")
        return
    email = doc["email"]
    queries = doc["queries"]
    response = doc["response"]
    response2 = doc["response2"]
    response3 = doc["response3"]
    last_updated = datetime.now()
    print('\n', type(email), type(queries), type(response), type(response2), type(response3), sep = '\n', end = '\n\n')
    
    try:
        new_uuid = genUUID()
        insrtQry = "INSERT INTO \"chat_history\" (id, user_email, queries, response, response2, response3, last_updated) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        
        cr.execute(insrtQry, (new_uuid, email, queries, response, response2, response3, last_updated))
        mycon.commit()

        print("insert_one ran successfully!")        
        
        
    except Exception as e:
        print("insert_one Error:", e)
        mycon.rollback()
    
    


def find_one():
    
    pass

def findAll():
    pass

def update_one():
    pass

def delete_many():
    pass
