from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DATABASE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    DRIVER: str
    SYNCDRIVER: str
    USERNAME: str
    PASSWORD: str
    HOSTNAME: str
    PORT: str
    NAME: str
    TESTNAME: str

    @property
    def async_url(self) -> str:
        driver, user, password, host, port, name = (
            self.DRIVER,
            self.USERNAME,
            self.PASSWORD,
            self.HOSTNAME,
            self.PORT,
            self.NAME,
        )
        return f"{driver}://{user}:{password}@{host}:{port}/{name}"

    @property
    def sync_url(self) -> str:
        driver, user, password, host, port, name = (
            self.SYNCDRIVER,
            self.USERNAME,
            self.PASSWORD,
            self.HOSTNAME,
            self.PORT,
            self.NAME,
        )
        return f"{driver}://{user}:{password}@{host}:{port}/{name}"


class MinioSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MINIO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    HOST: str
    ROOT_USER: str
    ROOT_PASSWORD: str
    PORT_API: str
    PORT_CONSOLE: str

    @property
    def url(self) -> str:
        host, port = (
            self.HOST,
            self.PORT_API,
        )
        return f"{host}:{port}"


class CelerySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CELERY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    DRIVER: str
    HOST: str
    PORT: str
    NAME: str

    @property
    def url(self) -> str:
        driver, host, port, name = (
            self.DRIVER,
            self.HOST,
            self.PORT,
            self.NAME,
        )
        return f"{driver}://{host}:{port}/{name}"


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AUTH_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int


database_settings = DatabaseSettings()
minio_settings = MinioSettings()
celery_settings = CelerySettings()
auth_settings = AuthSettings()
