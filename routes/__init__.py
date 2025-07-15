from .base import base_bp
from .workers import workers_bp
from .tokens import tokens_bp
from .sessions import sessions_bp
from .logs import logs_bp
from .statistic import statistic_bp
from .users_api import users_bp
from .sessions_info import session_info_bp


def register_blueprints(app):
    app.register_blueprint(base_bp)
    app.register_blueprint(workers_bp)
    app.register_blueprint(tokens_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(statistic_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(session_info_bp)
