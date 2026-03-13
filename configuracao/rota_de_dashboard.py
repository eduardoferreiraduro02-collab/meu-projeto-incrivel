from flask_sqlalchemy import SQLAlchemy

db = SQAlchemy()

def init_db(app):
  app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:senha@host:porta/database'

  db.init_app(app)