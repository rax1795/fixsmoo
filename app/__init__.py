from flask import Flask
from flask_bootstrap import Bootstrap
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
import logging
from logging.handlers import RotatingFileHandler
import os
# basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/img'
images = UploadSet('photos', IMAGES)
configure_uploads(app, images)
patch_request_class(app)  
# manager = Manager(app)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'

# if not app.debug:
#     # if not os.path.exists('logs'):
#     #     os.mkdir('logs')
#     # file_handler = RotatingFileHandler('logs/fixsmoo.log', maxBytes=10240,
#     #                                    backupCount=10)
#     # file_handler.setFormatter(logging.Formatter(
#     #     '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
#     # file_handler.setLevel(logging.INFO)
#     # app.logger.addHandler(file_handler)

#     # app.logger.setLevel(logging.INFO)
#     # app.logger.info('Fixsmoo startup')



from app import routes, models, forms, errors, chart_initialisation