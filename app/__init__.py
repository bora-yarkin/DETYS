from flask import Flask  # Flask'ı içe aktar
from app.core.config import Config  # Konfigürasyon ayarlarını içe aktar
from app.core.extensions import db, login_manager, migrate, mail, csrf  # Genişletmeleri içe aktar
from app.routes import register_routes  # Rotaları kaydet
from app.core.scheduler import scheduler  # Zamanlayıcıyı içe aktar
from flask_wtf.csrf import generate_csrf  # CSRF korumasını içe aktar


def create_app():
    app = Flask(__name__)  # Flask uygulamasını oluştur
    app.config.from_object(Config)  # Konfigürasyonu çağır

    # Flask genişletmelerini başlat
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)

    scheduler.init_app(app)
    scheduler.start()

    # Flask-Login yapılandırması
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)  # CSRF token'ını ekle

    register_routes(app)  # Rotaları kaydet

    return app
