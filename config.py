import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'postgresql://admins:pass@localhost:5432/fixsmoo1'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # UPLOADED_PHOTOS_DEST = os.getcwd()