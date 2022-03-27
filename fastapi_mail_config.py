from fastapi_mail import FastMail, MessageSchema,ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME = "fyndproject5@gmail.com",
    MAIL_PASSWORD = "Sidd@7021",
    MAIL_FROM = "fyndproject5@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)