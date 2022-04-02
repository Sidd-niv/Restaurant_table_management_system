import smtplib
from email.message import EmailMessage


# function to send mail with pdf
def send_mail(customer_mail: str):

    # Defining sender email address string
    Sender_Email = "fyndprojectrest333@gmail.com"

    # Defining receiver email address string
    Reciever_Email = customer_mail

    # Defining  email address password string
    Password = "fynd@#2612"

    # Defining EmailMessage class object
    newMessage = EmailMessage()

    # defining the content of email
    newMessage['Subject'] = "Hunger Fest Invoice"
    newMessage['From'] = Sender_Email
    newMessage['To'] = Reciever_Email
    newMessage.set_content('Thank you for visiting us')

    # defining the file name
    files = ['Invoice.pdf']

    # Write operation for email attachment
    for file in files:
        with open(file, 'rb') as f:
            file_data = f.read()
            file_name = f.name
        newMessage.add_attachment(file_data, maintype='application', subtype='octet-stream', filename="Invoice.pdf")

    # Sending email through smtplib
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(Sender_Email, Password)
        smtp.send_message(newMessage)





