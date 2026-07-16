from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VoiceOps API"
    environment: str = "development"
    debug: bool = False

    frontend_url: str
    database_url: str
    secret_key: str

    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    public_base_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()