from flask import Flask,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import login_user,login_required,LoginManager
from datetime import datetime
datetime.now().strftime('%Y-%m-%d %H:%M:%S')

db = SQLAlchemy()


def createApp():
    app = Flask(__name__, template_folder='template')
    
    if app.config["ENV"] == "production":
        app.config.from_object("config.ProductionConfig")
    else:
        app.config.from_object("config.DevelopmentConfig")

    print(f'ENV is set to: {app.config["ENV"]}')
    db.init_app(app)

    
    from .views import views
    from .auth import auth
    from .admin import admin
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/admin')
    
    
    from .model import Users,Vehicle,Repairs,Fuel

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'error'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))

    with app.app_context():
        db.create_all()
    migrate = Migrate(app,db)

    # import base64,os
    # def get_image_file_as_base64_data():
    #     path = os.path.dirname(os.path.abspath(__file__))
    #     print(path)
    #     with open( path + url_for('static',filename='assets/img/favicon.png'), 'rb') as image_file:
    #         return base64.b64encode(image_file.read())
    # app.jinja_env.globals.update(get_image_file_as_base64_data=get_image_file_as_base64_data)

    return app
