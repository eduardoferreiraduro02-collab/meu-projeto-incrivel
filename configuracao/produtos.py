from flask import Blueprint, request, jsonify
from sqlalchemy import text
from configuracao.database import db # Ajuste o caminho conforme seu projeto

erp_bp = Blueprint('erp', __name__, url_prefix='/erp')

# -------------------- CRUD ERP (PRODUTOS/SERVIÇOS) --------------------

# 1. Cadastrar Novo Pacote/Assinatura
@erp_bp.route("/produtos", methods=["POST"])
def criar_produto():
    nome_pacote = request.form.get("nome_pacote") # Ex: "Pacote Enem"
    preco = request.form.get("preco")             # Ex: 89.90
    qtd_correcoes = request.form.get("qtd_correcoes") # Ex: 4
    descricao = request.form.get("descricao")     # Ex: "Correções mensais"

    sql = text("""
        INSERT INTO produtos_erp 
            (nome_pacote, preco, qtd_correcoes, descricao, status_venda) 
        VALUES 
            (:nome, :preco, :qtd, :desc, 'Ativo') 
        RETURNING id
    """)
    
    params = {
        "nome": nome_pacote, 
        "preco": preco, 
        "qtd": qtd_correcoes, 
        "desc": descricao
    }

    try:
        result = db.session.execute(sql, params)
        db.session.commit()
        
        id_gerado = result.fetchone()[0]
        return {"id": id_gerado, "status": "Produto cadastrado com sucesso!"}, 201
    except Exception as e:
        db.session.rollback()
        return f"Erro ao cadastrar produto: {e}", 500


# 2. Listar Catálogo de Planos Ativos
@erp_bp.route("/catalogo")
def get_catalogo_ativo():
    # Filtra apenas o que está 'Ativo' para mostrar ao cliente final
    sql = text("SELECT * FROM produtos_erp WHERE status_venda = 'Ativo' ORDER BY preco ASC")
    
    try:
        result = db.session.execute(sql)
        produtos = result.mappings().all()
        return [dict(row) for row in produtos]
    except Exception as e:
        return str(e), 500


# 3. Buscar Detalhes de um Plano Específico
@erp_bp.route('/produtos/<id>')
def get_produto(id):
    sql = text("SELECT * FROM produtos_erp WHERE id = :id")
    
    try:
        result = db.session.execute(sql, {"id": id})
        linha = result.mappings().first()
        
        if linha:
            return dict(linha)
        return "Produto não encontrado", 404
    except Exception as e:
        return str(e), 500


# 4. Atualizar Preço ou Status do Pacote
@erp_bp.route("/produtos/<id>", methods=["PUT"])
def atualizar_produto(id):
    novo_preco = request.form.get("preco")
    novo_status = request.form.get("status_venda") # Ex: 'Pausado', 'Descontinuado'

    sql = text("""
        UPDATE produtos_erp 
        SET preco = :preco, status_venda = :status 
        WHERE id = :id
    """)
    
    try:
        db.session.execute(sql, {"preco": novo_preco, "status": novo_status, "id": id})
        db.session.commit()
        return f"Produto {id} atualizado no ERP."
    except Exception as e:
        db.session.rollback()
        return str(e), 500