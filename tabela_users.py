import psycopg2
import os

def insert_user(username, password, course, university):
    try:
        # Em um cenário real, use variáveis de ambiente para o host/pass
        conn = psycopg2.connect(
            host="localhost",
            database="seu_banco",
            user="postgres",
            password="sua_senha"
        )
        cur = conn.cursor()

        # Query usando Placeholders (%) para evitar SQL Injection
        sql = """
            INSERT INTO users (username, password_hash, target_course, target_university)
            VALUES (%s, %s, %s, %s) RETURNING id;
        """
        
        # O password aqui deve ser hasheado (ex: com bcrypt) antes de ir ao banco
        cur.execute(sql, (username, password, course, university))
        
        user_id = cur.fetchone()[0]
        conn.commit()
        
        print(f"Usuário {user_id} criado com sucesso!")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Erro na operação: {e}")

# Testando a função
insert_user('joao_estudante', 'senha123', 'Medicina', 'USP')

