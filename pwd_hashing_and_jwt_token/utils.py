from passlib.context import CryptContext

# Specifying the hashing algorithm for password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# function to return a hashing password
def get_Hash_pwd(user_pwd: str):
    if user_pwd:
        return pwd_context.hash(user_pwd)

# verifying the password by compare the password from clients side input with the pwd_context function since hashing
# is not reversible
def verify_pwd(user_pwd, hashed_pwd):
    return pwd_context.verify(user_pwd, hashed_pwd)
