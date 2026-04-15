from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from flask_cors import CORS

# --- DATABASE CONFIGURATION ---
DB_CONFIG = {
    'host': '127.0.0.1', 
    'user': 'root', 
    'password': 'Komal@123',
    'database': 'qbms_project'
}


app = Flask(__name__)
CORS(app)

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# ----------------------------------------------------------------------
# API ROUTES
# ----------------------------------------------------------------------

# 1. USER LOGIN AUTHENTICATION
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    if conn is None: return jsonify({"error": "DB connection failed"}), 500
    cursor = conn.cursor(dictionary=True)

    sql_query = "SELECT UserID, Username, Role, Password FROM Users WHERE Username = %s"
    
    try:
        cursor.execute(sql_query, (username,))
        user = cursor.fetchone()
        
        if user and user['Password'] == password: 
            return jsonify({
                "message": "Login successful", 
                "username": user['Username'], 
                "role": user['Role']
            }), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
            
    except Error as e:
        print(f"Database error during login: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500
    finally:
        cursor.close()
        conn.close()

# 2. COURSE LISTING (Used for dropdowns and search)
@app.route('/api/courses', methods=['GET'])
def get_courses():
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "DB connection failed"}), 500
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT CourseID, CourseName FROM Courses ORDER BY CourseName")
        courses = cursor.fetchall()
        return jsonify(courses), 200
    except Error as e:
        print(f"Database error fetching courses: {e}")
        return jsonify({"error": "Could not fetch courses."}), 500
    finally:
        cursor.close()
        conn.close()

# 3. CLO LISTING BY COURSE
@app.route('/api/clos/<string:course_id>', methods=['GET']) # Uses 'string' for alphanumeric CourseID
def get_clos_by_course(course_id):
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "DB connection failed"}), 500
    cursor = conn.cursor(dictionary=True)

    try:
        sql = "SELECT CLOID, CLOText, CourseID FROM CLOs WHERE CourseID = %s ORDER BY CLOID"
        cursor.execute(sql, (course_id,))
        clos = cursor.fetchall()
        return jsonify(clos), 200
    except Error as e:
        print(f"Database error fetching CLOs: {e}")
        return jsonify({"error": "Could not fetch CLOs."}), 500
    finally:
        cursor.close()
        conn.close()


# 4. ADD NEW CLO
@app.route('/api/clos', methods=['POST'])
def add_clo():
    data = request.get_json()
    # Assuming the front end sends CLOID manually for this route, based on the check_sql
    if not all(k in data for k in ('CourseID', 'CLOID', 'CLOText')):
        return jsonify({"error": "Missing required fields (CourseID, CLOID, CLOText)"}), 400

    conn = get_db_connection()
    if conn is None: return jsonify({"error": "DB connection failed"}), 500
    cursor = conn.cursor()

    # Check if CLO already exists for this course
    check_sql = "SELECT CLOID FROM CLOs WHERE CourseID = %s AND CLOID = %s"
    try:
        cursor.execute(check_sql, (data['CourseID'], data['CLOID']))
        if cursor.fetchone():
            return jsonify({"error": f"CLO-{data['CLOID']} already exists for this course."}), 409
            
        # Insert CLO
        insert_sql = "INSERT INTO CLOs (CLOID, CourseID, CLOText) VALUES (%s, %s, %s)"
        insert_data = (data['CLOID'], data['CourseID'], data['CLOText'])
        
        cursor.execute(insert_sql, insert_data)
        conn.commit()
        return jsonify({"message": "CLO added successfully"}), 201

    except Error as e:
        conn.rollback()
        print(f"Database error adding CLO: {e}")
        # Error 1452: Foreign Key constraint fails (CourseID doesn't exist)
        if e.errno == 1452: 
            return jsonify({"error": "Invalid CourseID: Course does not exist."}), 400
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# 5. QUESTION CREATION (UPDATED CODE BLOCK)
@app.route('/api/questions', methods=['POST'])
def create_question():
    data = request.get_json()
    
    # 1. Validate incoming data
    if not data: 
        return jsonify({"error": "No data provided"}), 400

    required_fields = ['question_text', 'q_type', 'difficulty', 'marks', 'clo_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field in JSON payload: {field}"}), 400

    # Ensure CLOID is an integer and Marks is a float/Decimal
    try:
        data['clo_id'] = int(data['clo_id'])
        data['marks'] = float(data['marks']) # Convert marks to float for validation/insertion
    except ValueError as e:
        return jsonify({"error": "Invalid format for CLOID or Marks."}), 400

    conn = get_db_connection()
    if conn is None: 
        return jsonify({"error": "DB connection failed"}), 500
    cursor = conn.cursor()
    
    try:
        # 2. Insert Question 
        question_sql = "INSERT INTO Questions (QuestionText, QuestionType, DifficultyLevel, Marks, CLOID) VALUES (%s, %s, %s, %s, %s)"
        question_data = (
            data['question_text'], 
            data['q_type'], 
            data['difficulty'], 
            data['marks'], 
            data['clo_id']
        )
        cursor.execute(question_sql, question_data)
        new_question_id = cursor.lastrowid
        
        # 3. Handle MCQ Options
        if data.get('q_type') == 'MCQ':
            options = data.get('options', [])
            if not options or len(options) < 2:
                 raise ValueError("MCQ type requires a list of at least two options.")
                 
            option_sql = "INSERT INTO Options (QuestionID, OptionText, IsCorrect) VALUES (%s, %s, %s)"
            for option in options:
                is_correct_val = 1 if option.get('is_correct') else 0 
                
                if 'text' not in option or not option['text'].strip():
                     raise ValueError("MCQ option text cannot be empty.")
                     
                option_data = (new_question_id, option['text'], is_correct_val) 
                cursor.execute(option_sql, option_data)

        # 4. Commit and Respond
        conn.commit()
        return jsonify({"message": "Question created successfully", "question_id": new_question_id}), 201
        
    except ValueError as ve:
        # Catch custom validation errors (like missing options for MCQ)
        conn.rollback()
        print(f"Validation error during question creation: {ve}")
        return jsonify({"error": "Validation failed.", "details": str(ve)}), 400
    except Error as e:
        conn.rollback()
        print(f"Database error during question creation: {e}") 
        # Check if the error is related to foreign key constraint (CLOID not found)
        if e.errno == 1452: 
            return jsonify({"error": "CLO Not Found. Ensure the selected CLO exists in the database."}, 
                           {"details": f"CLOID {data.get('clo_id')} does not exist or invalid."}), 400
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
# (END OF UPDATED CODE BLOCK)


# 6. FACULTY LISTING
@app.route('/api/faculty', methods=['GET'])
def get_faculty():
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "DB connection failed"}), 500
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT FacultyID, FacultyName FROM Faculty ORDER BY FacultyName")
        faculty_list = cursor.fetchall()
        return jsonify(faculty_list), 200
    except Error as e:
        print(f"Database error fetching faculty: {e}")
        return jsonify({"error": "Could not fetch faculty list."}), 500
    finally:
        cursor.close()
        conn.close()


# 7. PAPER LISTING WITH FILTERS
@app.route('/api/papers', methods=['GET'])
def get_papers():
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "DB connection failed"}), 500
    cursor = conn.cursor(dictionary=True)

    course_id = request.args.get('course_id')
    year = request.args.get('year')
    semester = request.args.get('semester')
    exam_type = request.args.get('exam_type')
    faculty_id = request.args.get('faculty_id')

    base_sql = """
        SELECT 
            p.PaperID, p.Year, p.Semester, p.ExamType, p.FacultyID,
            c.CourseName, f.FacultyName AS SetBy
        FROM PreviousYearPapers p 
        JOIN Courses c ON p.CourseID = c.CourseID
        JOIN Faculty f ON p.FacultyID = f.FacultyID
        WHERE 1=1
    """
    params = []

    if course_id:
        base_sql += " AND p.CourseID = %s"
        params.append(course_id)
    if year:
        base_sql += " AND p.Year = %s"
        params.append(year)
    if semester:
        base_sql += " AND p.Semester = %s"
        params.append(semester)
    if exam_type:
        base_sql += " AND p.ExamType = %s"
        params.append(exam_type)
    if faculty_id:
        base_sql += " AND p.FacultyID = %s"
        params.append(faculty_id)

    base_sql += " ORDER BY p.Year DESC, c.CourseName"

    try:
        cursor.execute(base_sql, tuple(params))
        papers = cursor.fetchall()

        formatted_papers = [
            {
                "PaperID": p['PaperID'],
                "CourseName": p['CourseName'],
                "Year": p['Year'],
                "Semester": p['Semester'],
                "ExamType": p['ExamType'],
                "SetBy": p['SetBy'],
                "SetByID": p['FacultyID'] 
            } for p in papers
        ]

        return jsonify(formatted_papers), 200

    except Error as e:
        print(f"Database error fetching papers: {e}")
        return jsonify({"error": "Could not fetch papers list."}), 500
    finally:
        cursor.close()
        conn.close()


# 8. GET PAPER CONTENT (MODIFIED to include MCQ Options and IsCorrect status)
@app.route('/api/papers/<int:paper_id>/content', methods=['GET'])
def get_paper_content(paper_id):
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "DB connection failed"}), 500
    # Use buffered=True to allow multiple queries (using a second cursor is safer)
    cursor = conn.cursor(dictionary=True, buffered=True) 

    try:
        # 1. Get Paper Metadata
        meta_sql = """
            SELECT
                p.PaperID, p.Year, p.Semester, p.ExamType,
                c.CourseName, c.CourseID, f.FacultyName AS Faculty
            FROM PreviousYearPapers p
            JOIN Courses c ON p.CourseID = c.CourseID
            JOIN Faculty f ON p.FacultyID = f.FacultyID
            WHERE p.PaperID = %s
        """
        cursor.execute(meta_sql, (paper_id,))
        metadata = cursor.fetchone()

        if not metadata:
            return jsonify({"message": f"Paper with ID {paper_id} not found."}), 404

        # 2. Get Questions for the Paper
        questions_sql = """
            SELECT 
                pq.QuestionID, q.QuestionText, q.QuestionType, q.Marks,
                clo.CLOText 
            FROM PaperQuestions pq
            JOIN Questions q ON pq.QuestionID = q.QuestionID
            JOIN CLOs clo ON q.CLOID = clo.CLOID
            WHERE pq.PaperID = %s
            ORDER BY pq.QuestionID
        """
        cursor.execute(questions_sql, (paper_id,))
        questions = cursor.fetchall()
        
        # SQL for fetching options
        options_sql = "SELECT OptionText, IsCorrect FROM Options WHERE QuestionID = %s ORDER BY OptionID"
        
        # Use a secondary cursor for fetching options within the loop
        options_cursor = conn.cursor(dictionary=True) 

        # 3. Process Questions and fetch options for MCQs
        for q in questions:
            # Format the CLO Text
            q['CLOText'] = q['CLOText'].split(' | ')[0]
            q['Options'] = [] 
            
            # Fetch options if it's an MCQ
            if q['QuestionType'] == 'MCQ':
                options_cursor.execute(options_sql, (q['QuestionID'],))
                q['Options'] = options_cursor.fetchall()
        
        options_cursor.close()

        return jsonify({
            "metadata": metadata,
            "questions": questions
        }), 200

    except Error as e:
        print(f"Database error fetching paper content: {e}")
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500
    finally:
        cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()


# 9. QUESTION SEARCH AND FILTER (Updated to support QuestionType and SearchText)
@app.route('/api/questions', methods=['GET'])
def search_questions():
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "DB connection failed"}), 500
    cursor = conn.cursor(dictionary=True)

    # Fetch all parameters
    course_id = request.args.get('course_id')
    clo_id = request.args.get('clo_id')
    difficulty = request.args.get('difficulty')
    question_type = request.args.get('question_type')
    search_text = request.args.get('search_text')

    base_sql = """
        SELECT 
            q.QuestionID, q.QuestionText, q.QuestionType, q.Marks, q.DifficultyLevel,
            c.CourseName,
            clo.CLOText
        FROM Questions q
        JOIN CLOs clo ON q.CLOID = clo.CLOID
        JOIN Courses c ON clo.CourseID = c.CourseID
        WHERE 1=1
    """
    params = []

    if course_id:
        base_sql += " AND c.CourseID = %s"
        params.append(course_id)
    if clo_id:
        base_sql += " AND q.CLOID = %s"
        params.append(clo_id)
    if difficulty:
        base_sql += " AND q.DifficultyLevel = %s"
        params.append(difficulty)

    if question_type:
        base_sql += " AND q.QuestionType = %s"
        params.append(question_type)
        
    if search_text:
        base_sql += " AND q.QuestionText LIKE %s"
        params.append(f"%{search_text}%")

    base_sql += " ORDER BY q.QuestionID DESC"
    
    try:
        cursor.execute(base_sql, tuple(params))
        questions = cursor.fetchall()

        for q in questions:
            if q.get('CLOText'):
                q['CLOText'] = q['CLOText'].split(' | ')[0] 
        
        return jsonify(questions), 200

    except Error as e:
        print(f"Database error fetching questions for student view: {e}")
        return jsonify({"error": "Could not fetch questions list.", "details": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# 10. GET QUESTION DETAILS (INCLUDING OPTIONS FOR MCQ)
@app.route('/api/questions/<int:question_id>/details', methods=['GET'])
def get_question_details(question_id):
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "DB connection failed"}), 500
    cursor = conn.cursor(dictionary=True)

    try:
        question_sql = """
            SELECT 
                q.QuestionID, q.QuestionText, q.QuestionType, q.Marks, q.DifficultyLevel,
                c.CourseName,
                clo.CLOID, clo.CLOText
            FROM Questions q
            JOIN CLOs clo ON q.CLOID = clo.CLOID
            JOIN Courses c ON clo.CourseID = c.CourseID
            WHERE q.QuestionID = %s
        """
        cursor.execute(question_sql, (question_id,))
        question = cursor.fetchone()

        if not question:
            return jsonify({"error": "Question not found"}), 404
        
        question['CLOText'] = question['CLOText'].split(' | ')[0]
        question['Options'] = [] 

        if question['QuestionType'] == 'MCQ':
            options_sql = "SELECT OptionID, OptionText, IsCorrect FROM Options WHERE QuestionID = %s ORDER BY OptionID"
            cursor.execute(options_sql, (question_id,))
            options = cursor.fetchall()
            question['Options'] = options

        return jsonify(question), 200

    except Error as e:
        print(f"Database error fetching question details: {e}")
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ----------------------------------------------------------------------
# --- PAPER MANAGEMENT ROUTES ----------------------------
# ----------------------------------------------------------------------

# 11. CREATE NEW PAPER (Metadata only)
@app.route('/api/papers/create', methods=['POST'])
def create_paper():
    data = request.get_json()
    # Check for required fields
    required_fields = ['CourseID', 'Year', 'Semester', 'ExamType', 'FacultyID']
    if not all(k in data for k in required_fields):
        return jsonify({"error": "Missing required paper metadata fields."}), 400

    conn = get_db_connection()
    if conn is None: return jsonify({"error": "DB connection failed"}), 500
    cursor = conn.cursor()

    sql = """
        INSERT INTO PreviousYearPapers 
        (CourseID, Year, Semester, ExamType, FacultyID) 
        VALUES (%s, %s, %s, %s, %s)
    """
    insert_data = (data['CourseID'], data['Year'], data['Semester'], data['ExamType'], data['FacultyID'])
    
    try:
        cursor.execute(sql, insert_data)
        conn.commit()
        new_paper_id = cursor.lastrowid
        return jsonify({
            "message": "Paper created successfully", 
            "paper_id": new_paper_id
        }), 201

    except Error as e:
        conn.rollback()
        print(f"Database error creating paper: {e}")
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 12. ADD QUESTION TO PAPER (Link existing question to paper)
@app.route('/api/papers/<int:paper_id>/questions', methods=['POST'])
def add_question_to_paper(paper_id):
    data = request.get_json()
    question_id = data.get('question_id')
    
    if not question_id:
        return jsonify({"error": "Missing required field: question_id"}), 400
        
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "DB connection failed"}), 500
    cursor = conn.cursor()

    # Query to link Question and Paper in the PaperQuestions junction table
    sql = "INSERT INTO PaperQuestions (PaperID, QuestionID) VALUES (%s, %s)"
    
    try:
        cursor.execute(sql, (paper_id, question_id))
        conn.commit()
        return jsonify({"message": f"Question {question_id} linked to Paper {paper_id} successfully."}), 201
        
    except Error as e:
        conn.rollback()
        # Handle duplicate entry error (e.g., MySQL error 1062)
        if e.errno == 1062:
            return jsonify({"error": "Question is already linked to this paper."}), 409
        
        print(f"Database error adding question to paper: {e}")
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 13. DELETE QUESTION FROM PAPER (Unlink question from paper)
@app.route('/api/papers/<int:paper_id>/questions/<int:question_id>', methods=['DELETE'])
def remove_question_from_paper(paper_id, question_id):
    conn = get_db_connection()
    if conn is None: return jsonify({"error": "DB connection failed"}), 500
    cursor = conn.cursor()

    sql = "DELETE FROM PaperQuestions WHERE PaperID = %s AND QuestionID = %s"
    
    try:
        cursor.execute(sql, (paper_id, question_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Question not found in this paper, or paper ID is invalid."}), 404
        
        return jsonify({"message": f"Question {question_id} removed from Paper {paper_id} successfully."}), 200
        
    except Error as e:
        conn.rollback()
        print(f"Database error removing question from paper: {e}")
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)