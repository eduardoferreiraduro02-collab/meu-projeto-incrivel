from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Configuração do Banco de Dados (PostgreSQL no Render)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:senha@host:port/database'
db = SQLAlchemy(app)

class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    meta = db.Column(db.String(255))
    foto_url = db.Column(db.String(255))

@app.route('/profile', methods=['PUT'])
def update_profile():
    # Em um sistema real, você pegaria o ID do usuário através do Token JWT
    user_id = 1 
    aluno = Aluno.query.get(user_id)

    if not aluno:
        return jsonify({"error": "Aluno não encontrado"}), 404

    data = request.get_json()

    # Atualiza a meta se enviada
    if 'meta' in data:
        aluno.meta = data['meta']
    
    # Atualiza a URL da foto se enviada
    if 'foto_url' in data:
        aluno.foto_url = data['foto_url']

    db.session.commit()

    return jsonify({
        "message": "Perfil atualizado com sucesso!",
        "aluno": {
            "meta": aluno.meta,
            "foto_url": aluno.foto_url
        }
    }), 200