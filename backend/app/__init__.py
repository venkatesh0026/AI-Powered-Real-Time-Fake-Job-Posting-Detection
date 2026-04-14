from flask import Flask
from .utils.config import Config
from .routes.health import health_bp
from .routes.inference import inference_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(inference_bp, url_prefix='/api')

    return app
