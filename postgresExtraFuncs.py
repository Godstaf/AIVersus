"""
Chat-history CRUD helpers (PostgreSQL).

Uses the shared per-request connection from db.py instead of a module-level
global connection/cursor, so a failed query can no longer leave a shared
connection stuck in an aborted-transaction state. All function signatures are
unchanged, so callers in app.py are unaffected.
"""

from datetime import datetime
import uuid

from db import get_cursor


def genUUID():
    """Return a UUID that isn't already used in chat_history."""
    while True:
        generated_uuid = str(uuid.uuid4())
        with get_cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM "chat_history" WHERE id = %s', (generated_uuid,))
            result = cur.fetchone()
        if result is not None and result[0] == 0:
            return generated_uuid


def insert_one(doc):
    if type(doc) != dict:
        print("Error: doc type is not Dict")
        return
    email = doc["email"]
    queries = doc["queries"]
    response = doc["response"]
    response2 = doc["response2"]
    response3 = doc["response3"]
    last_updated = datetime.now()

    try:
        new_uuid = genUUID()
        insrtQry = (
            'INSERT INTO "chat_history" '
            "(id, user_email, queries, response, response2, response3, last_updated) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        with get_cursor(commit=True) as cur:
            cur.execute(insrtQry, (new_uuid, email, queries, response, response2, response3, last_updated))
        print("insert_one ran successfully!")
        return new_uuid

    except Exception as e:
        print("insert_one Error:", e)
        return None


def find_one(id, email):
    result = None
    try:
        findQry = (
            "Select id, user_email, queries, response, response2, response3 "
            "from chat_history where id = %s and user_email = %s"
        )
        with get_cursor() as cur:
            cur.execute(findQry, (id, email))
            fetchedResult = cur.fetchone()
        if fetchedResult:
            result = {
                "id": fetchedResult[0], "email": fetchedResult[1], "queries": fetchedResult[2],
                "response": fetchedResult[3], "response2": fetchedResult[4], "response3": fetchedResult[5],
            }
        else:
            print("Result not found")

    except Exception as e:
        print("find_one Error:", e)

    return result


def findAll(email):
    result = None
    try:
        findQry = (
            "Select id, user_email, queries, response, response2, response3 "
            "from chat_history where user_email = %s"
        )
        with get_cursor() as cur:
            cur.execute(findQry, (email,))
            result = cur.fetchall()
        if result:
            for i in range(len(result)):
                result[i] = {
                    "id": result[i][0], "email": result[i][1], "queries": result[i][2],
                    "response": result[i][3], "response2": result[i][4], "response3": result[i][5],
                }  # type: ignore
        else:
            print("Result not found")

    except Exception as e:
        print("findAll Error:", e)

    return result


def update_one(id, email, qry='', rep='', rep2='', rep3=''):
    updateQry = (
        "UPDATE chat_history SET queries = array_append(queries, %s), "
        "response = array_append(response, %s), response2 = array_append(response2, %s), "
        "response3 = array_append(response3, %s), last_updated = %s WHERE id = %s"
    )
    try:
        with get_cursor(commit=True) as cur:
            cur.execute(updateQry, (qry, rep, rep2, rep3, datetime.now(), id))
        print("update_one ran successfully!")
        return True

    except Exception as e:
        print("update_one error:", e)
        return None


def delete_one(chat_id, email):
    """Delete a single chat by its ID and user email"""
    try:
        delQry = "DELETE FROM chat_history WHERE id = %s AND user_email = %s"
        with get_cursor(commit=True) as cur:
            cur.execute(delQry, (chat_id, email))
        print(f"Chat {chat_id} deleted successfully!")
        return True

    except Exception as e:
        print("delete_one error:", e)
        return None


def delete_many(email):
    try:
        delQry = "Delete from chat_history where user_email = %s and queries = \'{}\'"
        with get_cursor(commit=True) as cur:
            cur.execute(delQry, (email,))
        print("deleted successfully!")
        return 'Deletion successful'

    except Exception as e:
        print("delete_many error:", e)
        return None
