from flask import Flask

from config import Config

from .extensions import db, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    config_class.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)

    from .blueprints.finance.routes import finance_bp
    from .blueprints.students.routes import students_bp
    from .routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(students_bp, url_prefix="/alunos")
    app.register_blueprint(finance_bp, url_prefix="/financeiro")

    return app
