from flask import Flask, request, jsonify
from models import db, Essay

app = Flask(__name__)
# A URL abaixo você obterá no Render (PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:senha@host:port/database'
db.init_app(app)

# --- ROTAS DO CRUD ---

@app.route('/essays', methods=['POST'])
def create_essay():
    data = request.get_json()
    
    # Simulando que o ID do aluno vem no corpo ou via login (token)
    new_essay = Essay(
        title=data['title'],
        content=data['content'],
        student_id=data['student_id'] 
    )
    
    db.session.add(new_essay)
    db.session.commit()
    
    return jsonify({"message": "Redação enviada com sucesso!"}), 201

@app.route('/essays', methods=['GET'])
def get_essays():
    # Aqui filtramos pelo aluno logado (ex: passado via query param ou token)
    student_id = request.args.get('student_id')
    
    essays = Essay.query.filter_by(student_id=student_id).all()
    return jsonify([e.to_dict() for e in essays]), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Cria as tabelas se não existirem
    app.run(debug=True)