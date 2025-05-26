from flask import Flask, request, redirect, url_for, render_template_string
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import threading
import webview

app = Flask(__name__)

# Hardcoded SMTP credentials (for trusted environment)
#SMTP_USER = "kevinmshelly@gmail.com"
#SMTP_PASSWORD = "fvjryjztnzijrrls"
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

@app.route("/health")
def health():
    return "OK", 200

@app.route("/", methods=["GET", "POST"])
def send_emails():
    if request.method == "POST":
        # Handle file uploads
        excel_file = request.files.get("excel_file")
        image_file = request.files.get("image_file")
        pdf_file = request.files.get("pdf_file")
        message = request.form.get("message")

        if not excel_file:
            return "Please upload an Excel file.", 400

        try:
            # Read Excel data
            df = pd.read_excel(excel_file)
            if df.empty:
                return "Excel file is empty.", 400

            # Read image and PDF data once
            image_data = None
            pdf_data = None

            if image_file:
                try:
                    image_data = image_file.read()
                except Exception as e:
                    return f"Error reading image file: {e}", 500

            if pdf_file:
                try:
                    pdf_data = pdf_file.read()
                except Exception as e:
                    return f"Error reading PDF file: {e}", 500

            # Process each email
            for index, row in df.iterrows():
                email = row.get("Email", "")  # Adjust column name as needed
                if not email:
                    continue

                try:
                    # Create MIME message
                    msg = MIMEMultipart()
                    msg["From"] = SMTP_USER
                    msg["To"] = email
                    msg["Subject"] = "SAP is back - And Bigger than ever!"

                    # Attach message text
                    msg.attach(MIMEText(message, "plain"))

                    # Attach image file
                    if image_data:
                        img_part = MIMEApplication(image_data, _subtype="png")
                        img_part.add_header("Content-Disposition", "attachment", filename=image_file.filename)
                        msg.attach(img_part)

                    # Attach PDF file
                    if pdf_data:
                        pdf_part = MIMEApplication(pdf_data, _subtype="pdf")
                        pdf_part.add_header("Content-Disposition", "attachment", filename=pdf_file.filename)
                        msg.attach(pdf_part)

                    # Send email
                    with smtplib.SMTP("smtp.gmail.com", 587) as server:
                        server.starttls()
                        server.login(SMTP_USER, SMTP_PASSWORD)
                        server.sendmail(SMTP_USER, email, msg.as_string())

                except Exception as e:
                    print(f"Error sending to {email}: {e}")
                    continue

            return "Emails sent successfully!", 200
        except Exception as e:
            print(f"General error: {e}")
            return f"An error occurred: {e}", 500
    else:
        # Render form with image and PDF upload options
        return render_template_string("""
            <h2>Send Bulk Email with Attachments</h2>
            <form method="POST" enctype="multipart/form-data">
                <input type="file" name="excel_file" required accept=".xlsx, .xls"><br>
                <input type="file" name="image_file" accept=".png, .jpg"><br>
                <input type="file" name="pdf_file" accept=".pdf"><br>
                <textarea name="message" rows="4" cols="50" placeholder="Your message here..."></textarea><br>
                <button type="submit">Send Emails</button>
            </form>
        """)

#if __name__ == "__main__":
 #   app.run(debug=True)