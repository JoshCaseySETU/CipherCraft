from database import databaseConnect
import random
from flask import session, flash

def questions(module_number):
    query = f"SELECT Question, Option1, Option2, Option3, Option4, Correct FROM Quiz WHERE Module = '{module_number}'"
    result = databaseConnect(query)
    
    quiz_data = []
    correct_answers = []  # Initialize list to store correct answers
    
    if result:
        # Fetch up to 15 questions randomly
        questions_limit = min(len(result), 15)
        random_questions = random.sample(result, questions_limit)
        
        for row in random_questions:
            question_data = {
                'Question': row[0],
                'Option1': row[1],
                'Option2': row[2],
                'Option3': row[3],
                'Option4': row[4],
            }
            correct_answer = row[5]
            correct_answers.append(correct_answer)  # Store correct answer
            quiz_data.append(question_data)
            
        # Shuffle both quiz data and correct answers simultaneously
        combined_data = list(zip(quiz_data, correct_answers))
        random.shuffle(combined_data)
        quiz_data, correct_answers = zip(*combined_data)
        
        # Store correct answers in session
        session[f'correct_answers_{module_number}'] = correct_answers
    else:
        # Handle case where no quiz data is available for the requested module
        flash(f"No quiz data available for Module {module_number}.", 'warning')
    
    return quiz_data



def store_selected_option(question_index, selected_option):
    print("Storing selected option:", selected_option, "for question index:", question_index)
    # Retrieve or initialize the dictionary of selected options in the session
    selected_options = session.get('selected_options', {})
    # Store the selected option for the current question index in the dictionary
    selected_options[str(question_index)] = selected_option  # Convert to string
    session['selected_options'] = selected_options

def get_selected_option(question_index):
    # Retrieve the dictionary of selected options from the session
    selected_options = session.get('selected_options', {})
    # Retrieve the selected option for the current question index from the dictionary
    return selected_options.get(question_index, '')

def generate_new_quiz_data():
    module_number = session.get('module_num')
    return questions(module_number)

def add_question(module_number, question_text, options, correct_option):
    # Construct the SQL query to insert the new question into the database
    query = f"INSERT INTO Quiz (Module, Question, Option1, Option2, Option3, Option4, Correct) VALUES ('{module_number}', '{question_text}', '{options[0]}', '{options[1]}', '{options[2]}', '{options[3]}', '{correct_option}')"
    
    # Execute the query to insert the new question into the database
    databaseConnect(query)

def fetch_all_questions():
    query = "SELECT * FROM CipherCraft.Quiz"
    result = databaseConnect(query)
    
    all_questions = []
    for row in result:
        question_data = {
            'Module': row[1],
            'Question': row[2],
            'Option1': row[3],
            'Option2': row[4],
            'Option3': row[5],
            'Option4': row[6],
            'Correct': row[7]
        }
        all_questions.append(question_data)
        
    return all_questions


def filter_questions_by_module(module_number):
    query = f"SELECT * FROM Quiz WHERE Module = '{module_number}'"
    result = databaseConnect(query)
    
    filtered_questions = []
    for row in result:
        question_data = {
            'Module': row[1],
            'Question': row[2],
            'Option1': row[3],
            'Option2': row[4],
            'Option3': row[5],
            'Option4': row[6],
            'Correct': row[7]
        }
        filtered_questions.append(question_data)
        
    return filtered_questions


def edit_question(module_number, question_text, options, correct_option):
    # Construct the SQL query to update the question in the database
    query = f"UPDATE Quiz SET Option1 = '{options[0]}', Option2 = '{options[1]}', Option3 = '{options[2]}', Option4 = '{options[3]}', Correct = '{correct_option}' WHERE Module = '{module_number}' AND Question = '{question_text}'"
    
    # Execute the query to update the question in the database
    databaseConnect(query)

def delete_question(module_number, question_text):
    # Construct the SQL query to delete the question from the database
    query = f"DELETE FROM Quiz WHERE Module = '{module_number}' AND Question = '{question_text}'"
    
    # Execute the query to delete the question from the database
    databaseConnect(query)

def store_quiz_results(module_number, score_percentage):
    if 'username' in session:
        username = session['username']
        print(username)
        query_user_id = "SELECT userID FROM userInfo WHERE username = %s"
        result_user_id = databaseConnect(query_user_id, data=(username,), fetchone=True)
        if result_user_id:
            user_id = result_user_id[0]
            print(user_id)
                
    if user_id:
        query_insert_results = "INSERT INTO CipherCraft.Results (userID, Module, Result) VALUES (%s, %s, %s)"
        data = (user_id, module_number, score_percentage)
        databaseConnect(query_insert_results, data)

