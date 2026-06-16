import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/academia_financeiro",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        database_url = app.config["SQLALCHEMY_DATABASE_URI"]
        if database_url.startswith("postgres://"):
            app.config["SQLALCHEMY_DATABASE_URI"] = database_url.replace(
                "postgres://", "postgresql+psycopg://", 1
            )
        elif database_url.startswith("postgresql://"):
            app.config["SQLALCHEMY_DATABASE_URI"] = database_url.replace(
                "postgresql://", "postgresql+psycopg://", 1
            )
