from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3

customhost = "internshipdb.cjfu0ocm8ldv.us-east-1.rds.amazonaws.com"
customuser = "admin"
custompass = "admin123"
customdb = "internship"
custombucket = "hingzihui-internship"
customregion = "us-east-1"


app = Flask(__name__, static_folder='assets')

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}


    
@app.route("/SupervisorStudPage", methods=['GET', 'POST'])
def viewSupervisorStud():

    sv_id = "1";
    statement = "SELECT * FROM Supervisor WHERE sv_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (sv_id))
    result = cursor.fetchone()

    return render_template('supervisorStud.html' , supervisor=result)

@app.route('/')
def viewStudent():

    stud_id = "22WMR05651";
    statement = "SELECT * FROM Student WHERE stud_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (stud_id))
    result = cursor.fetchone()

    return render_template('student.html', student=result)

@app.route("/internshipPublication", methods=['GET', 'POST'])
def publichInternPage():
    return render_template('publishIntern.html')

@app.route("/addInternFormCom", methods=['POST'])
def AddInternFormCom():

    com_id = 1
    job_title = request.form['job_title']
    job_desc = request.form['job_description']
    job_salary = request.form['job_salary']
    job_location = request.form['job_location']
    workingDay = request.form['workingDay']
    workingHour = request.form['workingHour']
    accommodation = request.form['accommodation']
    
    #Get last ID
    countstatement = "SELECT intern_id FROM Internship ORDER BY intern_id DESC LIMIT 1;"
    count_cursor = db_conn.cursor()
    count_cursor.execute(countstatement)
    result = count_cursor.fetchone()
    intern_id = int(result[0]) + 1
    count_cursor.close()

    insert_sql = "INSERT INTO Internship VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

    try:
        # Attempt to execute the SQL INSERT statement
        cursor = db_conn.cursor()
        cursor.execute(insert_sql, (intern_id, com_id, job_title, job_desc, job_salary, job_location, workingDay, workingHour, accommodation))
        db_conn.commit()  # Commit the transaction
        cursor.close()
    except Exception as e:
        db_conn.rollback()  # Rollback the transaction in case of an error
        print(f"Error: {str(e)}")  # Print the error for debugging

    
    return render_template('publishInternSuccess.html', intern=job_title)


@app.route("/goManageInternship", methods=['GET'])
def GoManageInternship():

    com_id = 1
    statement = "SELECT intern_id, job_title, intern_salary FROM Internship WHERE com_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (com_id))

    result = cursor.fetchall()
    cursor.close()
    
    return render_template('manageIntern.html', data=result)

@app.route('/viewIntern/<int:internship_id>')
def view_internship(internship_id):

    statement = "SELECT * FROM Internship WHERE intern_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (internship_id))
    result = cursor.fetchone()

    return render_template('viewIntern.html', intern=result)

@app.route('/editIntern/<int:internship_id>')
def edit_internship(internship_id):

    statement = "SELECT * FROM Internship WHERE intern_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (internship_id))
    result = cursor.fetchone()

    return render_template('editIntern.html', intern=result)

        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
