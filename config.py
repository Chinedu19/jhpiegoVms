class Config(object):
    
    DEBUG = False
    TESTING = False
    SECRET_KEY = "whoisvms?"

    DB_NAME = "vmsdb"
    DB_USERNAME = "root"
    DB_PASSWORD = ""
    DB_HOST = "localhost"

    conn = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_DATABASE_URI = conn
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    ALLOWED_IMAGE_EXTENSION = ['PNG','PDF','JPG','JPEG']

    IMAGE_UPLOADS = "static\\uploads"

    SESSION_COOKIE_SECURE = True

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

    DB_NAME = "vmsdb"
    DB_USERNAME = "root"
    DB_PASSWORD = ""
    DB_HOST = "localhost"

    conn = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_DATABASE_URI = conn
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ALLOWED_IMAGE_EXTENSION = ['PNG','PDF','JPG','JPEG']

    IMAGE_UPLOADS = "static\\uploads"

    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    TESTING = True

    DB_NAME = "vmsdb"
    DB_USERNAME = "root"
    DB_PASSWORD = ""
    DB_HOST = "localhost"

    conn = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_DATABASE_URI = conn
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_IMAGE_EXTENSION = ['PNG','PDF','JPG','JPEG']
    IMAGE_UPLOADS = "static\\uploads"
    SESSION_COOKIE_SECURE = False