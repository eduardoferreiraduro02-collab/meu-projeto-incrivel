from flask import Flask
from configuracao.database import init_db

#Importar módulos 
from control.aluno import aluno_bp



app = Flask(__name__)

#Conexao Geral do meu app
init_db(app)

#Registro de controladores 
app.register_blueprint(aluno_bp)



if __name__ == "__main__":
    app.run(debug=True)
