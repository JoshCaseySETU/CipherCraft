from flask import session
from database import databaseConnect

def store_session_in_database():
    if 'username' in session:
        username = session['username']
        query_user_id = "SELECT userID FROM userInfo WHERE username = %s"
        result_user_id = databaseConnect(query_user_id, data=(username,))
        
        if result_user_id:
            user_id = result_user_id[0][0]
            module_num = session.get('module_num')
            topic_num = session.get('topic_num')
            page_num = session.get('page_num')

            # Check if the user already exists in userProgress table
            query_check_existence = "SELECT COUNT(*) FROM userProgress WHERE user_id = %s"
            result_count = databaseConnect(query_check_existence, data=(user_id,))
            
            if result_count and result_count[0][0] > 0:
                # If user exists, update the existing row
                query = "UPDATE userProgress SET module_num = %s, topic_num = %s, page_num = %s WHERE user_id = %s"
                databaseConnect(query, data=(module_num, topic_num, page_num, user_id))
                print("Session data updated in the database.", session['module_num'], session['topic_num'], session['page_num'])
            else:
                # If user doesn't exist, insert a new row
                query = "INSERT INTO userProgress (user_id, module_num, topic_num, page_num) VALUES (%s, %s, %s, %s)"
                databaseConnect(query, data=(user_id, module_num, topic_num, page_num))
                print("Session data stored in the database.")
        else:
            print("User not found.")
    else:
        print("Username not found in session.")

def fetch_user_progress():
    if 'username' in session:
        username = session['username']
        # Retrieve userID based on username
        query_user_id = "SELECT userID FROM userInfo WHERE username = %s"
        result_user_id = databaseConnect(query_user_id, data=(username,))
        
        if result_user_id:
            user_id = result_user_id[0][0]
            # Check if the user has made progress
            query_check_progress = "SELECT module_num, topic_num, page_num FROM userProgress WHERE user_id = %s"
            result_progress = databaseConnect(query_check_progress, data=(user_id,))
            
            if result_progress:
                # Progress found, populate session variables
                module_num, topic_num, page_num = result_progress[0]
                session['module_num'] = module_num
                session['topic_num'] = topic_num
                session['page_num'] = page_num
                print("Session variables populated with user progress.")
            else:
                # No progress found, let the route begin storing user progress
                print("No progress found for the user. Begin storing user progress in route.")
        else:
            print("User not found.")
    else:
        print("Username not found in session.")
