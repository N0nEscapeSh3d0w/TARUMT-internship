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

@app.route("/SupervisorStudPage", methods=['GET', 'POST'])
def viewSupervisorStud():

    sv_id = "1";
    statement = "SELECT * FROM Supervisor WHERE sv_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (sv_id))
    result = cursor.fetchone()

    return render_template('supervisorStud.html' , supervisor=result)

@app.route('/',  methods=['GET', 'POST'])
def mainSTud():

    stud_id = "22WMR05651";
    statement = "SELECT * FROM Student WHERE stud_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (stud_id))
    result = cursor.fetchone()

    return render_template('student.html', student=result)

@app.route('/viewStudent', methods=['GET', 'POST'])
def viewStudent():
    stud_id = "22WMR05651"
    statement = "SELECT * FROM Student WHERE stud_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(statement, (stud_id))
    result = cursor.fetchone()

    resume_key = "stud_id-" + str(stud_id) + "_pdf"

    s3 = boto3.client('s3', region_name=region)
    try:
        with BytesIO() as resume_buffer:
          
            resume_buffer.seek(0)

            # Return the PDF file
            response = send_file(
                resume_buffer,
                as_attachment=True,
                download_name="resume-" + str(stud_id) + "_pdf",
                mimetype='application/pdf'
            )
            return response

    except Exception as e:
        return str(e)
    finally:
        cursor.close()

    return render_template('student.html', student=result)
    
@app.route('/updateStudent',  methods=['POST'])
@csrf.exempt 
def update_Student():

    stud_id = "22WMR05651";
    programme = request.form['programme']
    student_group = request.form['grp']
    cgpa = request.form['cgpa']
    password = request.form['password']
    intern_batch = request.form['intern_batch']

    currentAddress = request.form['currentAddress']
    contactNo = request.form['contactNo']
    personalEmail = request.form['personalEmail']
    homeAddress = request.form['homeAddress']
    homePhone = request.form['homePhone']
    resume = request.files['resume']

    if resume.filename != "":
        # Check if a file was uploaded
        if 'resume' in request.files:
            resume = request.files['resume']
        
            # Check if the uploaded file is allowed
            if resume and allowed_file(resume.filename):
                cursor = db_conn.cursor()
                resume_in_s3 = "stud_id-" + str(stud_id) + "_pdf"
                s3 = boto3.resource('s3')
    
                try:
                    print("Data inserted in MySQL RDS... uploading pdf to S3...")
                    s3.Bucket(custombucket).put_object(Key=resume_in_s3, Body=resume, ContentType=resume.content_type)
            
                   # Generate the object URL
                    object_url = f"https://{custombucket}.s3.amazonaws.com/{resume_in_s3}"
                    statement = "UPDATE Student SET programme = %s, grp = %s, cgpa = %s, password = %s, intern_batch = %s, currentAddress = %s, contactNo = %s, personalEmail = %s, homeAddress = %s, homePhone = %s, resume = %s WHERE stud_id = %s;"
                    cursor.execute(statement, (programme, student_group, cgpa, password, intern_batch, currentAddress, contactNo, personalEmail, homeAddress, homePhone, object_url, stud_id))
                    db_conn.commit()  # Commit the changes to the database
                    
                    return render_template('/viewStudent')
                except Exception as e:
                    return str(e)
                finally:
                    cursor.close()
            else:
              return "Invalid file format. Allowed formats are: " + ", ".join(ALLOWED_EXTENSIONS)
    else:
        update_statement = "UPDATE Student SET programme = %s, grp = %s, cgpa = %s, password = %s, intern_batch = %s, currentAddress = %s, contactNo = %s, personalEmail = %s, homeAddress = %s, homePhone = %s WHERE stud_id = %s;"
        ud_cursor = db_conn.cursor()
        ud_cursor.execute(update_statement, (programme, student_group, cgpa, password, intern_batch, currentAddress, contactNo, personalEmail, homeAddress, homePhone, stud_id))
        db_conn.commit()  # Commit the changes to the database
        return render_template('/viewStudent')
            

    return "No file uploaded."

if __name__ == '__main__':
    app.secret_key = 'hingzihui_key'
    app.run(host='0.0.0.0', port=80, debug=True)
