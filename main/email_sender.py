import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

def send_email(recipient, subject, body, attachment_path):
    try:
        msg = MIMEMultipart()
        msg['From'] = "your_email@example.com"
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with open(attachment_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {attachment_path}")
        msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("your_email@example.com", "your_password")
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Additional functions for email formatting, scheduling, etc.