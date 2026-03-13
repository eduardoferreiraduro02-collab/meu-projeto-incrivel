from flask import Blueprint, request, jsonify
from sqlalchemy import text
from configuracao.database import db # Ajuste o caminho conforme seu projeto

aluno_bp = Blueprint('aluno', __name__, url_prefix='/aluno')

# -------------------- CRUD ALUNO (FOCO EM RETENÇÃO) --------------------

# Criar Aluno (Matrícula com Meta de Curso)
@aluno_bp.route("/", methods=["POST"])
def criar_aluno():
    nome = request.form.get("nome")
    meta_curso = request.form.get("meta_curso")
    universidade = request.form.get("universidade_alvo")
    ano_escolar = request.form.get("ano_escolar")

    sql = text("""
        INSERT INTO alunos 
            (nome, meta_curso, universidade_alvo, ano_escolar, status_retencao) 
        VALUES 
            (:nome, :meta, :uni, :ano, 'Ativo') 
        RETURNING id
    """)
    
    params = {
        "nome": nome, 
        "meta": meta_curso, 
        "uni": universidade, 
        "ano": ano_escolar
    }

    try:
        result = db.session.execute(sql, params)
        db.session.commit()
        
        id_gerado = result.fetchone()[0]
        return {"id": id_gerado, "status": "Aluno matriculado com sucesso!"}, 201
    except Exception as e:
        db.session.rollback()
        return f"Erro ao matricular: {e}", 500

# Listar Alunos em Risco (Lógica de Retenção)
# Filtra alunos que o status não seja 'Ativo' para o professor agir
@aluno_bp.route("/alerta-retencao")
def get_alunos_em_risco():
    sql = text("SELECT * FROM alunos WHERE status_retencao != 'Ativo'")
    
    try:
        result = db.session.execute(sql)
        relatorio = result.mappings().all()
        return [dict(row) for row in relatorio]
    except Exception as e:
        return str(e), 500

# Buscar Aluno por ID (Para ver a Meta e Universidade)
@aluno_bp.route('/<id>')
def get_aluno(id):
    sql = text("SELECT * FROM alunos WHERE id = :id")
    
    try:
        result = db.session.execute(sql, {"id": id})
        linha = result.mappings().first()
        
        if linha:
            return dict(linha)
        return "Aluno não encontrado", 404
    except Exception as e:
        return str(e), 500

# Atualizar Dados/Meta do Aluno
@aluno_bp.route("/<id>", methods=["PUT"])
def atualizar_aluno(id):
    meta = request.form.get("meta_curso")
    status = request.form.get("status") # Ex: 'Em Risco', 'Evasão', 'Ativo'

    sql = text("UPDATE alunos SET meta_curso = :meta, status_retencao = :status WHERE id = :id")
    
    try:
        result = db.session.execute(sql, {"meta": meta, "status": status, "id": id})
        db.session.commit()
        return f"Dados do aluno {id} atualizados."
    except Exception as e:
        db.session.rollback()
        return str(e), 500