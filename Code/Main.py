import os
from flask import Flask, session, redirect, url_for, render_template, request, jsonify
from flask_bcrypt import Bcrypt
from auth import signUp, Login, assign_unauthenticated_token 
from content import fetch_content, next_page_func, prev_page_func, is_module_completed, fetch_module_content, update_page_content, has_passed_quiz
from quiz import questions, get_selected_option, store_selected_option, generate_new_quiz_data, add_question, edit_question,delete_question, filter_questions_by_module, store_quiz_results
from progress import store_session_in_database, fetch_user_progress
from profile_functions import get_results
from datetime import timedelta
    
app = Flask(__name__)
app.secret_key = os.environ.get('sessionKey')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

bcrypt = Bcrypt(app)
    

@app.route('/')
def home():
    if 'authenticated' not in session:
        if 'unauthenticated_token' not in session:
            assign_unauthenticated_token()
        
    return render_template("home.html")

@app.route('/signUp', methods=['GET', 'POST'])
def signUpPage():
    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        confirmEmail = request.form['confirmEmail']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']
 
        return signUp(username, email, confirmEmail, password, confirmPassword, bcrypt)

    return render_template("auth.html", is_login=False)

# Login page route 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        return Login(username, password, bcrypt)

    return render_template("auth.html", is_login=True)

@app.route('/content', methods=['GET', 'POST'])
def content():
    
    fetch_user_progress()
    if session.get('module_num') is None: 
        session['module_num'] = 1
        session['topic_num'] = 1
        session['page_num'] = 1
    
    module_num = session['module_num']
    topic_num = session['topic_num']
    page_num = session['page_num']
    print(module_num, topic_num, page_num)
    
    # Check if the user has passed the previous module
    previous_module_num = module_num - 1
    if previous_module_num > 0 and not has_passed_quiz(previous_module_num):
        # Update the module_num session variable to the previous module
        session['module_num'] = previous_module_num
        # Redirect the user to the quiz
        return redirect(url_for('default_quiz')) 

    content_data = fetch_content(module_num, topic_num, page_num)
    completed_module = is_module_completed(module_num, topic_num, page_num)

    return render_template("contentPage.html", content_data=content_data, completed_module=completed_module)

@app.route('/update_session/<module_number>/<topic_number>')
def update_session(module_number, topic_number):
    session['module_num'] = module_number
    session['topic_num'] = topic_number
    session['page_num'] = 1
    store_session_in_database()
    return redirect(url_for('content'))

   
@app.route('/prev_page')
def prev_page_route():
    module_num = session['module_num']
    topic_num = session['topic_num']
    page_num = session['page_num']
    
    module_num, topic_num, page_num = prev_page_func(module_num, topic_num, page_num)
    session['module_num'] = module_num
    session['topic_num'] = topic_num
    session['page_num'] = page_num
    
    store_session_in_database()
    return redirect(url_for('content'))

@app.route('/next_page')  # Update the route to use underscore notation
def next_page_route():
    module_num = session['module_num']
    topic_num = session['topic_num']
    page_num = session['page_num']
    
    module_num, topic_num, page_num = next_page_func(module_num, topic_num, page_num)
    session['module_num'] = module_num
    session['topic_num'] = topic_num
    session['page_num'] = page_num
    
    store_session_in_database()
    return redirect(url_for('content'))
 
# Logout route 
@app.route('/logout', methods=['GET'])
def logout():

    session.clear()
    response = jsonify({'success': True})
    response.delete_cookie('session')
    return redirect(url_for('home'))

@app.route('/quiz/<module_number>/<int:question_index>', methods=['GET', 'POST'])
def quiz(module_number, question_index):
    
    if not session.get('in_quiz'):
        return redirect(url_for('home'))
    
    # Grabs the questions based on the module
    quiz_data = session.get('quiz_data')  # Retrieve quiz data from session

    if not quiz_data:  # If quiz data is not stored in session, generate and store it
        quiz_data = questions(module_number)
        session['quiz_data'] = quiz_data

    num_questions = len(quiz_data)
    current_question = quiz_data[int(question_index) - 1]  # Convert to integer
    prev_question = int(question_index) - 1 if int(question_index) > 1 else None  # Convert to integer
    next_question = int(question_index) + 1 if int(question_index) < num_questions else None  # Convert to integer

    if request.method == 'POST':
        print(request.form)
        # Retrieve the selected option and question index from the form submission
        selected_option = request.form.get('selected_option')
        print(selected_option)
        question_index = int(request.form.get('question_index'))  # Convert to integer
        # Store the selected option for the current question
        store_selected_option(question_index, selected_option)

    quiz_progress = (int(question_index) / num_questions) * 100
    # Retrieve the selected option for the current question
    selected_option = get_selected_option(question_index)
    
    

    return render_template("quiz.html", current_question=current_question, prev_question=prev_question,
                           next_question=next_question, module_number=module_number, selected_option=selected_option, current_question_index=question_index, progress=quiz_progress)
    
@app.route('/quiz', methods=['GET', 'POST'])
def default_quiz():
    
    if 'in_quiz' in session and session['in_quiz']:
        # Redirect to the homepage
        return redirect(url_for('home'))
    else:
        # If 'in_quiz' session does not exist, set it and redirect to the quiz
        session['in_quiz'] = True
        # Redirect to the first question of the first module
        return redirect(url_for('quiz', module_number='1', question_index=1))


@app.route('/results')
def results():
    session.pop('in_quiz', None)
    
    # Retrieve the module number from the session
    module_number = session.get('module_num')
    
    # Retrieve the selected options and correct answers for the specific module from the session
    selected_options = session.get('selected_options', {})
    print(selected_options)
    correct_answers = session.get(f'correct_answers_{module_number}', [])
    print(correct_answers)
    
    num_correct = 0
    for index, selected_option in selected_options.items():
        try:
            correct_answer_index = int(index) - 1
            if correct_answer_index >= 0 and correct_answer_index < len(correct_answers):
                if selected_option == correct_answers[correct_answer_index]:
                    num_correct += 1
        except IndexError:
            print("IndexError occurred for index:", index)

# Calculate the percentage score
    total_questions = len(correct_answers)
    print(total_questions)
    score_percentage = (num_correct / total_questions) * 100 if total_questions > 0 else 0
    print(score_percentage)

    return render_template("results.html", num_correct=num_correct, total_questions=total_questions, score_percentage=score_percentage)

@app.route('/retake_quiz', methods=['POST', 'GET'])
def retake_quiz():
    print("Retaking quiz...")
    if 'in_quiz' in session:
        # Print session data before clearing
        print("Session data before clearing:", session)
        
        # Clear all quiz-related session data
        session.pop('quiz_data', None)  
        session.pop('selected_options', None)  
        session.pop('correct_answers', None)  
        session.pop('in_quiz', None)  

        # Generate new quiz data and set it in the session
        session['in_quiz'] = True
        session['quiz_data'] = generate_new_quiz_data()
        print("New quiz data:", session['quiz_data'])

        # Print session data after clearing
        print("Session data after clearing:", session)

    # Redirect to the quiz route to start the quiz again
    return redirect(url_for('default_quiz'))

@app.after_request
def add_cache_control(response):
    if session.get('in_quiz'):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        # Handle form submission here (update_questions)
        for key in request.form:
            if key.startswith('question_text_'):
                index = key.split('_')[-1]
                # Get the corresponding updated values from the form
                question_text = request.form['question_text_' + index]
                option1 = request.form['option1_' + index]
                option2 = request.form['option2_' + index]
                option3 = request.form['option3_' + index]
                option4 = request.form['option4_' + index]
                correct_option = request.form['correct_option_' + index]
                # Call the edit_question function to update the question in the database
                edit_question(request.form['module_number'], question_text, [option1, option2, option3, option4], correct_option)
        # Handle adding new question here
        if 'new_question_text' in request.form:
            module_number = request.form['module_number']
            question_text = request.form['new_question_text']
            options = [
                request.form['new_option1'],
                request.form['new_option2'],
                request.form['new_option3'],
                request.form['new_option4']
            ]
            correct_option = request.form['new_correct_option']
            add_question(module_number, question_text, options, correct_option)
            return redirect(url_for('admin'))
    # Fetch questions based on the selected module number
    module_number = request.args.get('module_number', '1')  # Default to module 1 if not specified
    questions = filter_questions_by_module(module_number)  # Implement this function to fetch questions by module from the database
    return render_template('admin.html', questions=questions, module_number=module_number)

@app.route('/delete_question', methods=['POST'])
def delete_question_route():
    module_number = request.form['module_number']
    question_text = request.form['question_text']
    # Call the delete_question function passing the module_number and question_text
    delete_question(module_number, question_text)
    return redirect(url_for('admin'))

@app.route('/fetch_module', methods=['POST', 'GET'])
def fetch_module():
    module_num = request.form['module_number']
    content = fetch_module_content(module_num)
    if content:
        return render_template('admin.html', content=content)
    else:
        return "Error: Module not found."

# New route to update page content
@app.route('/update_page', methods=['POST'])
def update_page():
    module_num = request.form['module_number']
    topic_id = request.form['topic_id']
    page_id = request.form['page_id']
    new_content = request.form['new_content']
    success = update_page_content(module_num, topic_id, page_id, new_content)
    if success:
        return redirect(url_for('admin'))
    else:
        return "Error: Failed to update page content."

@app.route('/profile', methods=['POST', 'GET'])
def profile_page():
   
    results = get_results()
    
    return render_template("profile.html", results=results)
    
if __name__ == "__main__":
    app.run()