from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from curses import flash
from flask_wtf.csrf import CSRFProtect, CSRFError
from pymysql import connections
import os
import boto3
import botocore
import pdfplumber
# Use BytesIO to handle the binary content
from io import BytesIO
from flask import send_file
from werkzeug.utils import secure_filename

customhost = "internshipdb.cjfu0ocm8ldv.us-east-1.rds.amazonaws.com"
customuser = "admin"
custompass = "admin123"
customdb = "internship"
custombucket = "hingzihui-internship"
customregion = "us-east-1"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

app = Flask(__name__, static_folder='assets')
#encrypt
csrf = CSRFProtect(app)

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
def allowed_file(filename):
    _, file_extension = os.path.splitext(filename)
    return file_extension.lower()[1:] in ALLOWED_EXTENSIONS

@app.route("/SupervisorStudPage/<string:stud_id>")
def viewSupervisorStud(stud_id):

    statement = "SELECT * FROM Student WHERE stud_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (stud_id))
    result = cursor.fetchone()

    statement = "SELECT sv_id FROM Student_List WHERE stud_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (stud_id,))
    result1 = cursor.fetchone()

    if result1 is not None:
        sv_id = result1[0]

        statement = "SELECT * FROM Supervisor WHERE sv_id = %s"
        cursor.execute(statement, (sv_id,))
        result2 = cursor.fetchone()

        if result2 is not None:
            return render_template('supervisorStud.html', student= result, supervisor=result2)

    # Handle the case where no results were found or an error occurred
    return "Supervisor not found."

@app.route('/',  methods=['GET', 'POST'])
def mainStud():

    stud_id = "22WMR05651";
    statement = "SELECT * FROM Student WHERE stud_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (stud_id))
    result = cursor.fetchone()

    return render_template('student.html', student=result)

@app.route('/viewStudent/<string:stud_id>')
def viewStudent(stud_id):

    statement = "SELECT * FROM Student WHERE stud_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (stud_id))
    result = cursor.fetchone()

    return render_template('student.html', student=result)

@app.route('/studentEditPage/<string:stud_id>')
def studentEditPage(stud_id):

    statement = "SELECT * FROM Student WHERE stud_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (stud_id))
    result = cursor.fetchone()

    return render_template('studentEdit.html', student=result)
    
@app.route('/updateStudent/<string:stud_id>')
@csrf.exempt 
def update_Student(stud_id):

    programme = request.form['programme']
    student_group = request.form['grp']
    cgpa = request.form['cgpa']
    password = request.form['password']
    intern_batch = request.form['intern_batch']
    ownTransport = request.form['ownTransport']
    currentAddress = request.form['currentAddress']
    contactNo = request.form['contactNo']
    personalEmail = request.form['personalEmail']
    homeAddress = request.form['homeAddress']
    homePhone = request.form['homePhone']
    profile_img = request.form['profile_img']
    resume = request.files['resume']

    if profile_img.filename != "":
        profile_img_in_s3 = "stud_id-" + str(stud_id) + "_png"
        s3 = boto3.resource('s3')
        s3.Bucket(custombucket).put_object(Key=profile_img_in_s3, Body=profile_img, ContentType=profile_img.content_type)
        profile_img_url = f"https://{custombucket}.s3.amazonaws.com/{profile_img_in_s3}"
         
    if resume.filename != "":
        resume_in_s3 = "stud_id-" + str(stud_id) + "_pdf"
        s3 = boto3.resource('s3')
        s3.Bucket(custombucket).put_object(Key=resume_in_s3, Body=resume, ContentType=resume.content_type)
        resume_url = f"https://{custombucket}.s3.amazonaws.com/{resume_in_s3}"
    
    #no change in profile_img and resume
    if profile_img.filename == "" and resume.filename == "":
        statement = "UPDATE Student SET programme = %s, grp = %s, cgpa = %s, password = %s, intern_batch = %s, ownTransport = %s, currentAddress = %s, contactNo = %s, personalEmail = %s, homeAddress = %s, homePhone = %s WHERE stud_id = %s;"
        cursor = db_conn.cursor()
        cursor.execute(statement, (programme, student_group, cgpa, password, intern_batch, ownTransport, currentAddress, contactNo, personalEmail, homeAddress, homePhone, stud_id))
        db_conn.commit()  # Commit the changes to the database
    
    #only change in resume
    elif profile_img.filename == "" and resume.filename != "":
        statement = "UPDATE Student SET programme = %s, grp = %s, cgpa = %s, password = %s, intern_batch = %s, ownTransport = %s, currentAddress = %s, contactNo = %s, personalEmail = %s, homeAddress = %s, homePhone = %s, resume = %s WHERE stud_id = %s;"
        cursor = db_conn.cursor()
        cursor.execute(statement, (programme, student_group, cgpa, password, intern_batch, ownTransport, currentAddress, contactNo, personalEmail, homeAddress, homePhone, resume_url, stud_id))
        db_conn.commit()  # Commit the changes to the database 
    
        #only change in profile_img
    elif profile_img.filename != "" and resume.filename == "":
        statement = "UPDATE Student SET programme = %s, grp = %s, cgpa = %s, password = %s, intern_batch = %s, ownTransport = %s, currentAddress = %s, contactNo = %s, personalEmail = %s, homeAddress = %s, homePhone = %s, profile_img = %s WHERE stud_id = %s;"
        cursor = db_conn.cursor()
        cursor.execute(statement, (programme, student_group, cgpa, password, intern_batch, ownTransport, currentAddress, contactNo, personalEmail, homeAddress, homePhone, profile_img_url, stud_id))
        db_conn.commit()  # Commit the changes to the database 
    
    #change both
    else:
        statement = "UPDATE Student SET programme = %s, grp = %s, cgpa = %s, password = %s, intern_batch = %s, ownTransport = %s, currentAddress = %s, contactNo = %s, personalEmail = %s, homeAddress = %s, homePhone = %s, resume = %s, profile_img = %s WHERE stud_id = %s;"
        cursor = db_conn.cursor()
        cursor.execute(statement, (programme, student_group, cgpa, password, intern_batch, ownTransport, currentAddress, contactNo, personalEmail, homeAddress, homePhone, profile_img_url, resume_url, stud_id))
        db_conn.commit()  # Commit the changes to the database 
    
    return redirect('/viewStudent/stud_id')

@app.route('/submitReport/<string:stud_id>')
@csrf.exempt 
def submit_Report(stud_id):

    #Get last ID
    countstatement = "SELECT report_id FROM Report ORDER BY report_id DESC LIMIT 1;"
    count_cursor = db_conn.cursor()
    count_cursor.execute(countstatement)
    result = count_cursor.fetchone()
    report_id = int(result[0]) + 1
    count_cursor.close()

    report_title = request.form['report_title']
    report_type = request.form['report_type']
    report = request.files['report']
    
    if report.filename != "":
        # Check if a file was uploaded
        if 'report' in request.files:
            report = request.files['report']
        
            # Check if the uploaded file is allowed
            if report and allowed_file(report.filename):
                cursor = db_conn.cursor()
                report_in_s3 = "report_id-" + str(report_id) + "_pdf"
                s3 = boto3.resource('s3')
    
                try:
                    print("Data inserted in MySQL RDS... uploading pdf to S3...")
                    s3.Bucket(custombucket).put_object(Key=report_in_s3, Body=report, ContentType=report.content_type)
            
                   # Generate the object URL
                    object_url = f"https://{custombucket}.s3.amazonaws.com/{report_in_s3}"
                    insert_sql = "INSERT INTO Report VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(insert_sql, (report_id, stud_id, report_title, report_type, object_url))
                    db_conn.commit()  # Commit the changes to the database
                    
                    return redirect('/SupervisorStudPage')
                except Exception as e:
                    return str(e)
                finally:
                    cursor.close()
            else:
              return "Invalid file format. Allowed formats are: " + ", ".join(ALLOWED_EXTENSIONS)

    return "No file uploaded."
    
if __name__ == '__main__':
    app.secret_key = 'hingzihui_key'
    app.run(host='0.0.0.0', port=80, debug=True)
