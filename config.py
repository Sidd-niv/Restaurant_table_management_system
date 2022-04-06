from pydantic import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    secert_key: str
    algorithm: str
    access_token_expire_time: int
    sender_email: str
    password: str

    class Config:
        env_file = ".env"


setting = Settings()
