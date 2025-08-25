from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "User Management Service"
    DATABASE_URL: str = "postgresql://user:password@localhost/db"
    SECRET_KEY: str = "a-very-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
