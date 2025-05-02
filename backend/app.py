from flask import Flask, request, send_file   # Imports Flask to create the appliation, requests data from the user and sends files (PDF) back to the user
from flask_cors import CORS # Imports CORS to allow cross-origin requests (for frontend and backend communication)
from report_generator import generate_pdf # Imports the function from report generator to generate PDF reports
import smtplib # This is the library used to send emails
from email.message import EmailMessage # This is the library used to create email messages
import json # This is the library used to handle reading data in JSON 
from datetime import datetime # This is the library used to get the current date and time
import os # This is the library used to handle file and directory operations

app = Flask(__name__)  # Creates the Flask application
CORS(app) # Enables CORS for the application (Important for frontend-backend communication)

# This is the Function to send the User's PDF via email
def send_email_with_pdf(to_email, pdf_path, data):   # This function sends the email with the PDF attached
    email_address = "gdprcomplianceresults1@gmail.com"  # Admin email address
    email_password = "kryuabczynuogngr"   # Gmail admin password

    msg = EmailMessage()  # Creates a new email message
    msg["Subject"] = "Your GDPR Compliance Report & Recommendations"  # Sets the subject of the email
    msg["From"] = email_address  # Sets the admins email address
    msg["To"] = to_email  # Sets the recipient's email address
    msg.set_content(f"""  
Dear {data.get('name', 'User')},

Thank you for using our GDPR Compliance Checker.

Attached to this email is your personalised GDPR compliance report, based on your responses to key questions related to Articles 5 and 6 of the General Data Protection Regulation.

This report outlines your current compliance status and highlights potential areas for improvement.

If you have any questions or would like to discuss your results in more detail, feel free to reply to this email.

Kindest regards,  
GDPR Compliance Team
""")
    # This is the automatic email message that is sent to the user.

    # Attach PDF to email function
    with open(pdf_path, "rb") as f:  # Opens the PDF file in binary read mode
        pdf_data = f.read()  # Reads the PDF data
        msg.add_attachment(pdf_data, maintype="application", subtype="pdf", filename="gdpr_compliance_report.pdf")  # Attaches the PDF to the email
   
    # Send via Gmail SMTP
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp: # Connects to the Gmail server 
        smtp.login(email_address, email_password) # Logs in to the admin account
        smtp.send_message(msg) # Sends the email message

@app.route("/submit", methods=["POST"]) # This is the route that handles the form submission from the frontend
def submit(): # This is the function that handles the form submission
    data = request.json # Gets the submitted JSON data from the request

    # STEP 1: Prepare storage folder
    os.makedirs("submissions", exist_ok=True) # Creates a sub-directory called "submissions"
    log_file = "submissions/all_submissions.json" # This is the file where all the submissions are stored

    # Loads existing submissions
    if os.path.exists(log_file): # Checks if the log file exists
        with open(log_file, "r") as f:  # Opens the log file in read mode
            submissions = json.load(f)  # Loads the existing submissions from the log file
    else: 
        submissions = [] # If the log file does not exist, creates an empty list for submissions

    # STEP 2: Create a copy of the data inputed exluding the entered name and email
    anonymised_data = {key: value for key, value in data.items() if key.lower() not in ["name", "email"]} # This creates a copy of the data excluding the name and email fields
    anonymised_data["submitted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # This adds the current date and time to the data

    # Saves only anonymised answers
    submissions.append(anonymised_data) 

    with open(log_file, "w") as f: # Opens the log file in write mode
        json.dump(submissions, f, indent=2) # Saves the updated submissions to the log file

    # STEP 3: Calculate compliance score (using original data)
    question_fields = [k for k in data.keys() if k.lower() not in ["name", "email", "submitted_at"]] # This creates a list of question fields ignoring the name, email and submitted_at fields
    score = sum(1 for k in question_fields if data[k].strip().lower() == "yes") # This calculates the score based on the number of "yes" answers
    percentage = int((score / len(question_fields)) * 100) # This calculates the percentage of compliance based on the score and the number of questions

    # STEP 4: Calculate Compliance & Generate the PDF report
    if percentage >= 80:
        status = "Compliant"
    elif percentage >= 50:
        status = "Partially Compliant"
    else:
        status = "Non-Compliant"
# This determines the compliance status based on the percentage score
    pdf_path = generate_pdf(data, percentage, status) # This generates the PDF report using the data, percentage and status

    # STEP 5: Email PDF to user and admin
    user_email = data.get("email") # This gets the user's email from the submitted data
    if user_email: # Checks if the user has provided an email address
        send_email_with_pdf(user_email, pdf_path, data) # Sends the PDF to the user's email address
    send_email_with_pdf("gdprcomplianceresults1@gmail.com", pdf_path, data) # Sends the PDF to the admin's email address

    # STEP 6: Return the PDF file to browser as a downloadable file
    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__": 
    app.run(debug=True)  # Runs the Flask application in debug mode