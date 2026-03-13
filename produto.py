from flask import Flask, Blueprint, request
from sqlalchemy import text

from conf.database import db

produto_bp = Blueprint('produto', __name__, url_prefix = '/produto') 


# -------------------- CRUD PRODUTO --------------------
# Criar retornando ID (Insert com Returning)
@produto_bp.route("/", methods=["POST"])
def criar_produto_com_id():
    # dados que vieram
    nome = request.form.get("nome")
    valor = request.form.get("valor")

    # SQL
    sql = text("""
                INSERT INTO produtos 
                    (nome_produto, preco, marca_id) 
                VALUES 
                    (:nome, :valor, :marca_id) 
                RETURNING id
                """)
    dados = {"nome": nome, "valor": valor, "marca_id": marca}

    try:
        # executar consulta
        result = db.session.execute(sql, dados)
        db.session.commit()

        # pega o id
        id_gerado = result.fetchone()[0]
        dados['id'] = id_gerado
        
        return dados
    except Exception as e:
        return f"Erro: {e}"

# Ler um (Select by ID)
@produto_bp.route('/<id>')
def get_produto(id):
    sql = text("SELECT * FROM produtos WHERE id = :id")
    dados = {"id": id}
    
    try:
        result = db.session.execute(sql, dados)
        # Mapear todas as colunas para a linha
        linhas = result.mappings().all()
        
        if len(linhas) > 0:
            return dict(linhas[0])
        else:
            return "Produto não encontrado"
            
    except Exception as e:
        return str(e)

# Ler todos (Select All)
@produto_bp.route('/all')
def get_all_produtos():
    sql_query = text("SELECT * FROM produtos")
    
    try:
        result = db.session.execute(sql_query)
        
        relatorio = result.mappings().all()
        json_output = [dict(row) for row in relatorio] # Converte linhas em lista de dicionários

        return json_output
    except Exception as e:
        return []

# Atualizar (Update)
@produto_bp.route("/<id>", methods=["PUT"])
def atualizar_produto(id):
    # dados que vieram
    nome = request.form.get("nome")
    valor = request.form.get("valor")

    sql = text("UPDATE produtos SET nome_produto = :nome, preco = :valor WHERE id = :id")
    dados = {"nome": nome, "valor": valor, "id": id}

    try:
        result = db.session.execute(sql, dados)
        linhas_afetadas = result.rowcount 
        
        if linhas_afetadas == 1: 
            db.session.commit()
            return f"Produto {id} atualizado com sucesso"
        else:
            db.session.rollback()
            return f"Produto não encontrado ou erro ao atualizar"
    except Exception as e:
        return str(e)

# Deletar (Delete)
@produto_bp.route("/<id>", methods=['DELETE'])
def delete_produto(id):
    sql = text("DELETE FROM produtos WHERE id = :id")
    dados = {"id": id}
    
    try:
        result = db.session.execute(sql, dados)
        linhas_afetadas = result.rowcount 
        
        if linhas_afetadas == 1: 
            db.session.commit()
            return f"Produto {id} removido"
        else:
            db.session.rollback()
            return f"Erro: Produto não encontrado para deletar"
    except Exception as e:
        return str(e)