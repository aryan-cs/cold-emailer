import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

GMAIL_USER = "aryan.cs.app@gmail.com"
GMAIL_PASSWORD = "btjk conk pxxm zlkm"
TEMPLATE_FILE = "aryan.txt"
SIGNATURE_HTML = """
    <div><div><b style="color:rgb(136,136,136)"><span>Aryan Gupta</span></b></div></div>
    <div><div><div style="color:rgb(136,136,136)">
        <span style="font-size:12.8px">CompE &amp; Stats || AI/Mathematics Research</span><br>
    </div><div><span style="font-size:12.8px"><u><a href="https://github.com/aryan-cs" target="_blank">
        <font color="#3d85c6">https://github.com/aryan-cs</font></a></u></span></div></div></div>
"""

def send_email(company_name, role_name, company_email):
    subject = f"{role_name} Internship Role at {company_name}"
    with open(TEMPLATE_FILE, "r") as file:
        body_text = file.read()

    body_text = body_text.replace("{{COMPANY_NAME}}", company_name)
    body_text = body_text.replace("{{ROLE_NAME}}", role_name)
    body_text = body_text.replace("\n", "<br>")

    body = f"""<html>
    <head>
        <style>
            body {{
                color: black;
                font-family: Arial, sans-serif;
            }}
            .signature {{
                color: rgb(136,136,136);
                font-size: 12.8px;
            }}
        </style>
    </head>
    <body>
        <p>{body_text}</p>
        <div class="signature">
            {SIGNATURE_HTML}
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = company_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    filename = "resume.pdf"
    try:
        with open(filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)

            part.add_header(
                "Content-Disposition", f"attachment; filename={filename}"
            )
            msg.attach(part)
    except FileNotFoundError:
        print("Resume file not found. Please ensure 'resume.pdf' is in the correct path.")

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, company_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)

company = input("Company Name > ")
role = input("Role Name > ")
company_email = input("Company Email > ")

send_email(company, role, company_email)
