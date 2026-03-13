from flask import Blueprint, request, jsonify
from sqlalchemy import text
from configuracao.database import db # Mantendo o seu padrão de importação

produto_bp = Blueprint('produto', __name__, url_prefix='/produto')

# -------------------- CRUD ERP (PRODUTOS / SERVIÇOS) --------------------

# 1. Cadastrar Novo Pacote ou Assinatura (Ex: Pacote Enem)
@produto_bp.route("/", methods=["POST"])
def criar_produto():
    nome = request.form.get("nome")
    tipo = request.form.get("tipo") # 'Assinatura' ou 'Pacote'
    preco = request.form.get("preco")
    limite_correcoes = request.form.get("limite_correcoes")

    sql = text("""
        INSERT INTO produtos 
            (nome, tipo, preco, limite_correcoes, status_disponivel) 
        VALUES 
            (:nome, :tipo, :preco, :limite, True) 
        RETURNING id
    """)
    
    params = {
        "nome": nome, 
        "tipo": tipo, 
        "preco": preco, 
        "limite": limite_correcoes
    }

    try:
        result = db.session.execute(sql, params)
        db.session.commit()
        
        id_gerado = result.fetchone()[0]
        return {"id": id_gerado, "status": f"Produto '{nome}' cadastrado no ERP!"}, 201
    except Exception as e:
        db.session.rollback()
        return f"Erro ao cadastrar produto: {e}", 500

# 2. Listar Todos os Planos Ativos (Para o Aluno escolher)
@produto_bp.route("/")
def listar_catalogo():
    sql = text("SELECT * FROM produtos WHERE status_disponivel = True")
    
    try:
        result = db.session.execute(sql)
        produtos = result.mappings().all()
        return [dict(row) for row in produtos]
    except Exception as e:
        return str(e), 500

# 3. Buscar Detalhes de um Plano Específico
@produto_bp.route('/<id>')
def get_produto(id):
    sql = text("SELECT * FROM produtos WHERE id = :id")
    
    try:
        result = db.session.execute(sql, {"id": id})
        linha = result.mappings().first()
        
        if linha:
            return dict(linha)
        return "Produto não encontrado", 404
    except Exception as e:
        return str(e), 500

# 4. Atualizar Preço ou Limite de Correções
@produto_bp.route("/<id>", methods=["PUT"])
def atualizar_produto(id):
    preco = request.form.get("preco")
    limite = request.form.get("limite_correcoes")

    sql = text("""
        UPDATE produtos 
        SET preco = :preco, limite_correcoes = :limite 
        WHERE id = :id
    """)
    
    try:
        db.session.execute(sql, {"preco": preco, "limite": limite, "id": id})
        db.session.commit()
        return f"Produto {id} atualizado com sucesso."
    except Exception as e:
        db.session.rollback()
        return str(e), 500