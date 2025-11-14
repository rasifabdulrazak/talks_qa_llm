from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    # App config
    APP_NAME: str = "APIs for questionnaire chatbot using pdf"
    DEBUG: bool = True
    
    # DB Config
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DATABASE_URL: str

    # jwt config
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE: int = 30
    
    # Redis config
    REDIS_HOST:str
    REDIS_PORT:int
    REDIS_PASSWORD:str
    
    # LLM config
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    LLM_PROVIDER: str
    LLM_MODEL: str
    MAX_TOKEN: int
    LLM_API_KEY: str
    TEMPERATURE:float
    
settings = Settings()