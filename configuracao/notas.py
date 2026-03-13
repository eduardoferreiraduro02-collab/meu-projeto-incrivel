from flask import Blueprint, request, jsonify
from sqlalchemy import text
from datetime import datetime, timedelta
from configuracao.database import db 

aluno_bp = Blueprint('aluno', __name__, url_prefix='/aluno')

# -------------------- REGRAS DE NEGÓCIO (ENTREGAS E MÉDIA) --------------------

@aluno_bp.route("/<int:id>/entrega", methods=["POST"])
def registrar_entrega_redacao(id):
    """
    REGRA: Ao registrar uma nota, atualiza a 'average_grade' (Média Geral)
    e a 'data_ultima_interacao' para evitar o Status de Risco.
    """
    nota = request.form.get("grade", type=float)
    tema = request.form.get("essay_theme")
    feedback = request.form.get("feedback_summary")
    data_hoje = datetime.now()

    try:
        # 1. Inserir na tabela 'entregas_redacao' (Antiga interactions)
        sql_entrega = text("""
            INSERT INTO entregas_redacao (aluno_id, grade, essay_theme, feedback_summary, data_entrega) 
            VALUES (:id, :grade, :theme, :feedback, :data)
        """)
        db.session.execute(sql_entrega, {
            "id": id, "grade": nota, "theme": tema, 
            "feedback": feedback, "data": data_hoje
        })

        # 2. Recalcular Média e Atualizar data na tabela 'alunos' (Antiga leads)
        # O status volta para 'Ativo' automaticamente pois houve interação
        sql_update_aluno = text("""
            UPDATE alunos 
            SET average_grade = (SELECT AVG(grade) FROM entregas_redacao WHERE aluno_id = :id),
                data_ultima_interacao = :data,
                status_retencao = 'Ativo'
            WHERE id = :id
        """)
        db.session.execute(sql_update_aluno, {"id": id, "data": data_hoje})
        
        db.session.commit()
        return {"status": "Redação registrada! Média e interação atualizadas."}, 200

    except Exception as e:
        db.session.rollback()
        return f"Erro ao registrar entrega: {e}", 500


@aluno_bp.route("/processar-risco-inatividade", methods=["POST"])
def verificar_inatividade_15_dias():
    """
    REGRA: Alunos sem entrega há mais de 15 dias ficam 'Em Risco'.
    """
    prazo = datetime.now() - timedelta(days=15)

    sql_risco = text("""
        UPDATE alunos 
        SET status_retencao = 'Em Risco' 
        WHERE data_ultima_interacao < :prazo 
        AND status_retencao = 'Ativo'
    """)

    try:
        result = db.session.execute(sql_risco, {"prazo": prazo})
        db.session.commit()
        return {"mensagem": f"{result.rowcount} alunos agora estão em Risco de Evasão."}, 200
    except Exception as e:
        db.session.rollback()
        return str(e), 500

# -------------------- CRUD ALUNOS (ADAPTADO) --------------------

@aluno_bp.route("/", methods=["POST"])
def criar_aluno():
    nome = request.form.get("nome")
    meta = request.form.get("meta_curso")
    uni = request.form.get("target_university") # Campo extra solicitado
    ano = request.form.get("ano_escolar")

    sql = text("""
        INSERT INTO alunos 
            (nome, meta_curso, target_university, ano_escolar, status_retencao, data_ultima_interacao, average_grade) 
        VALUES 
            (:nome, :meta, :uni, :ano, 'Ativo', :data, 0.0) 
        RETURNING id
    """)
    
    try:
        result = db.session.execute(sql, {
            "nome": nome, "meta": meta, "uni": uni, 
            "ano": ano, "data": datetime.now()
        })
        db.session.commit()
        return {"id": result.fetchone()[0], "status": "Aluno matriculado!"}, 201
    except Exception as e:
        db.session.rollback()
        return str(e), 500

@aluno_bp.route("/alerta-retencao")
def get_alunos_em_risco():
    sql = text("SELECT * FROM alunos WHERE status_retencao = 'Em Risco'")
    result = db.session.execute(sql)
    return jsonify([dict(row) for row in result.mappings().all()])