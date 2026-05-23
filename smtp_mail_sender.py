import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import  secrets
load_dotenv()

def send_email(email,subject,message, link  ) :
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = os.getenv("SMTP_SENDER_EMAIL")
    msg['To'] = email
    msg.set_content(message)

    html = f"""
    <html>
        <body style="font-family: Arial; background:#f4f4f4; padding:20px;">
            <div style="
                max-width:600px;
                margin:auto;
                background:white;
                padding:30px;
                border-radius:10px;
                box-shadow:0 0 10px rgba(0,0,0,0.1);
            ">
                <h2 style="color:#2563eb;">Hello 👋</h2>

                <p style="font-size:16px; color:#333;">
                    {message}
                </p>

                <div style="margin-top:30px;">
                    <a href="{link}"
                       style="
                            background:#2563eb;
                            color:white;
                            padding:12px 20px;
                            text-decoration:none;
                            border-radius:6px;
                            display:inline-block;
                       ">
                        Open BD-pay
                    </a>
                </div>
            </div>
        </body>
    </html>
    """

    msg.add_alternative(html, subtype="html")
    with smtplib.SMTP_SSL(os.getenv("SMTP_MAIL_SERVER"), 465) as smtp:
        smtp.login(os.getenv("SMPT_USERNAME"), os.getenv("SMTP_PASSWORD"))
        smtp.send_message(msg)

def generate_otp():
        return str(secrets.randbelow(900000) + 100000)
if __name__=="__main__" :
    send_email("kobirbiddut81@gmail.com", "I don't know", "This is body of my first email.")


