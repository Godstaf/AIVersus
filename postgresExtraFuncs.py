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
        return new_uuid
        
        
    except Exception as e:
        print("insert_one Error:", e)
        mycon.rollback()
        return None
    
    


def find_one(id, email):
    result = None
    try:
        findQry = "Select id, user_email, queries, response, response2, response3 from chat_history where id = %s and user_email = %s"
        cr.execute(findQry, (id, email))
        fetchedResult = cr.fetchone()
        if fetchedResult:
            result = {"id": fetchedResult[0], "email": fetchedResult[1], "queries": fetchedResult[2], "response": fetchedResult[3], "response2": fetchedResult[4], "response3": fetchedResult[5]}
            print("Result found:", result)
        else:
            print("Result not found")
            
    except Exception as e:
        print("find_one Error:", e)
        mycon.rollback()
    
    return result
    

def findAll(email):
    result = None
    try:
        findQry = "Select id, user_email, queries, response, response2, response3 from chat_history where user_email = %s"
        cr.execute(findQry, (email,))
        result = cr.fetchall()
        if result:
            for i in range(len(result)):
                result[i] = {"id": result[i][0], "email": result[i][1], "queries": result[i][2], "response": result[i][3], "response2": result[i][4], "response3": result[i][5]} # type: ignore
            print("Result found:", result)
        else:
            print("Result not found")
            
    except Exception as e:
        print("findAll Error:", e)
        mycon.rollback()
        
    return result



def update_one(id, email, qry='', rep='', rep2='', rep3=''):
    
    # Demo query
    """UPDATE chat_history SET queries = array_append(queries, 'This is a new query string.') WHERE id = 'e2f03b78-f0c1-40ce-a95d-26d54acc863e"""
    
    updateQry = "UPDATE chat_history SET queries = array_append(queries, %s), response = array_append(response, %s), response2 = array_append(response2, %s), response3 = array_append(response3, %s), last_updated = %s WHERE id = %s"
    try:
        cr.execute(updateQry, (qry, rep, rep2, rep3, datetime.now(), id))
        mycon.commit()
        print("update_one ran successfully!")
        return True

    except Exception as e:
        print("update_one error:", e)
        mycon.rollback
        return None
    

def delete_many(email):
    try:
        delQry = "Delete from chat_history where user_email = %s and queries = \'{}\'"
        cr.execute(delQry, (email, ))
        mycon.commit()
        print("deleted successfully!")
        return 'Deletion successful'
        
    except Exception as e:
        print("delete_many error:", e)
        mycon.rollback()
        return None

