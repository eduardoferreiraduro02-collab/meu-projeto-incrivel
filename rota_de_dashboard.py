from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)

# Configuração da conexão com o PostgreSQL (Render fornece essa URL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:senha@host:porta/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definição do Modelo para o Banco de Dados
class Nota(db.Model):
    __tablename__ = 'notas'
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    data_criacao = db.Column(db.DateTime, server_default=func.now())

# Rota solicitada: GET /dashboard/stats
@app.route('/dashboard/stats', methods=['GET'])
def get_stats():
    try:
        # 1. Lógica para Média Geral
        media_geral = db.session.query(func.avg(Nota.valor)).scalar()
        
        # 2. Lógica para Última Nota (ordenando pela data ou ID)
        ultima_nota_obj = Nota.query.order_by(Nota.data_criacao.desc()).first()
        ultima_nota = ultima_nota_obj.valor if ultima_nota_obj else 0

        return jsonify({
            "media_geral": round(media_geral, 2) if media_geral else 0,
            "ultima_nota": ultima_nota
        }), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)