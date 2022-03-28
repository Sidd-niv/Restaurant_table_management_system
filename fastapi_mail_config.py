import smtplib
from email.message import EmailMessage

def send_mail(customer_mail: str):
    Sender_Email = "fyndprojectrest333@gmail.com"
    Reciever_Email = customer_mail
    Password = "fynd@#2612"

    newMessage = EmailMessage()
    newMessage['Subject'] = "Hunger Fest Invoice"
    newMessage['From'] = Sender_Email
    newMessage['To'] = Reciever_Email
    newMessage.set_content('Thank you for visiting us')

    files = ['Invoice.pdf']

    for file in files:
        with open(file, 'rb') as f:
            file_data = f.read()
            file_name = f.name
        newMessage.add_attachment(file_data, maintype='application', subtype='octet-stream', filename="Invoice.pdf")
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(Sender_Email, Password)
        smtp.send_message(newMessage)





