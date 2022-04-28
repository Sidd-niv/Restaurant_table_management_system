import smtplib
from email.message import EmailMessage
from config import setting

# function to send mail with pdf
def send_mail(customer_mail: str):

    # Defining sender email address string
    sender_email = setting.sender_email

    # Defining receiver email address string
    reciever_email = customer_mail

    # Defining  email address password string
    # Password = "fynd@#2612"
    Password = setting.password

    # Defining EmailMessage class object
    newMessage = EmailMessage()

    # defining the content of email
    newMessage['Subject'] = "Hunger Fest Invoice"
    newMessage['From'] = sender_email
    newMessage['To'] = reciever_email
    newMessage.set_content('Thank you for visiting us')

    # defining the file name
    files = ['Invoice.pdf']

    # Write operation for email attachment
    for file in files:
        with open(file, 'rb') as f:
            file_data = f.read()
            file_name = f.name
        newMessage.add_attachment(file_data, maintype='application', subtype='octet-stream', filename="../Invoice.pdf")

    # Sending email through smtplib
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, Password)
        smtp.send_message(newMessage)





