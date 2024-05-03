from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    BOT_TOKEN: str
    ADMIN_ID: int
        
    # DB_URL: str

    @property
    def DATABASE_URL(self):
        return f"sqlite+aiosqlite:///database.db"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()