from flask import Blueprint, request, jsonify
from sqlalchemy import text
from datetime import datetime, timedelta
from configuracao.database import db 

produto_bp = Blueprint('produto', __name__, url_prefix='/produto')

# -------------------- REGRAS DE NEGÓCIO: PRODUTO --------------------

@produto_bp.route("/<int:id>/entrada", methods=["POST"])
def registrar_entrada_estoque(id):
    """
    REGRA 1: Ao registrar nova entrada, recalcula o Custo Médio Unitário
    e atualiza a data da última movimentação.
    """
    valor_compra = request.form.get("valor_compra", type=float)
    data_hoje = datetime.now()

    try:
        # 1. Registra a movimentação de entrada
        sql_mov = text("""
            INSERT INTO movimentacoes (produto_id, valor, tipo, data_mov) 
            VALUES (:id, :valor, 'ENTRADA', :data)
        """)
        db.session.execute(sql_mov, {"id": id, "valor": valor_compra, "data": data_hoje})

        # 2. Recalcula a Média de Custo do Produto e reseta status de risco
        sql_produto = text("""
            UPDATE produtos 
            SET custo_medio = (SELECT AVG(valor) FROM movimentacoes WHERE produto_id = :id AND tipo = 'ENTRADA'),
                data_ultima_venda = :data,
                status_comercial = 'Giro Normal'
            WHERE id = :id
        """)
        db.session.execute(sql_produto, {"id": id, "data": data_hoje})
        
        db.session.commit()
        return {"status": "Estoque atualizado e custo médio recalculado!"}, 200

    except Exception as e:
        db.session.rollback()
        return f"Erro ao processar entrada: {e}", 500


@produto_bp.route("/verificar-estoque-parado", methods=["POST"])
def verificar_produtos_parados():
    """
    REGRA 2: Se o produto não tem saída (venda) há mais de 15 dias,
    muda o status para 'Estoque Parado'.
    """
    limite_data = datetime.now() - timedelta(days=15)

    sql_parado = text("""
        UPDATE produtos 
        SET status_comercial = 'Estoque Parado' 
        WHERE data_ultima_venda < :limite 
        AND status_comercial = 'Giro Normal'
    """)

    try:
        result = db.session.execute(sql_parado, {"limite": limite_data})
        db.session.commit()
        return {"mensagem": f"{result.rowcount} produtos marcados como 'Estoque Parado'."}, 200
    except Exception as e:
        db.session.rollback()
        return str(e), 500

# -------------------- CRUD DE PRODUTOS --------------------

@produto_bp.route("/", methods=["POST"])
def criar_produto():
    nome = request.form.get("nome")
    categoria = request.form.get("categoria")
    
    sql = text("""
        INSERT INTO produtos 
            (nome, categoria, status_comercial, data_ultima_venda, custo_medio) 
        VALUES 
            (:nome, :cat, 'Giro Normal', :data, 0.0) 
        RETURNING id
    """)
    
    try:
        result = db.session.execute(sql, {
            "nome": nome, 
            "cat": categoria, 
            "data": datetime.now()
        })
        db.session.commit()
        return {"id": result.fetchone()[0], "status": "Produto cadastrado!"}, 201
    except Exception as e:
        db.session.rollback()
        return str(e), 500

@produto_bp.route("/relatorio-risco")
def get_produtos_parados():
    sql = text("SELECT * FROM produtos WHERE status_comercial = 'Estoque Parado'")
    result = db.session.execute(sql)
    return jsonify([dict(row) for row in result.mappings().all()])