from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def init_db(app):

                                                                    #usuario:senha@servidor(host)/bancodedados
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:123@localhost/aula'

    db.init_app(app)