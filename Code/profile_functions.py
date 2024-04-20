from flask import session
from database import databaseConnect

def get_results():
    if 'username' in session:
        username = session['username']
        query_user_id = "SELECT userID FROM userInfo WHERE username = %s"
        result_user_id = databaseConnect(query_user_id, data=(username,), fetchone=True)
        if result_user_id:
            user_id = result_user_id[0]
            if user_id:
                query_quiz_results = "SELECT * Result FROM CipherCraft.Results WHERE userID = %s"
                result_scores = databaseConnect(query_quiz_results, data=(user_id))
                return result_scores
        return result_scores


