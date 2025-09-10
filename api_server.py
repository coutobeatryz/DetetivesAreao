import os
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Habilita o CORS para permitir que a Unity (de qualquer origem) se comunique com a API
CORS(app)

# Pega a URL de conexão do banco de dados das variáveis de ambiente configuradas no Render
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Cria e retorna uma nova conexão com o banco de dados."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# --- Rotas da API ---

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    apelido = data.get('apelido')
    senha = data.get('senha')
    nome = data.get('nome')
    # Outros campos como sobrenome, data_nascimento, tipo_pessoa podem ser adicionados aqui

    if not apelido or not senha or not nome:
        return jsonify({"status": "erro", "mensagem": "Nome, apelido e senha são obrigatórios"}), 400

    hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "erro", "mensagem": "Não foi possível conectar ao banco de dados"}), 500

    try:
        cursor = conn.cursor()
        
        # Insere em 'profiles'
        sql_insert_profile = """
            INSERT INTO profiles (id, nome, apelido, tipo_pessoa, senha_hash) 
            VALUES (gen_random_uuid(), %s, %s, 'aluno', %s) RETURNING id;
        """
        cursor.execute(sql_insert_profile, (nome, apelido, hashed_password.decode('utf-8')))
        new_user_id = cursor.fetchone()[0]

        # Insere em 'alunos'
        sql_insert_aluno = "INSERT INTO alunos (id_profile) VALUES (%s);"
        cursor.execute(sql_insert_aluno, (new_user_id,))
        
        conn.commit()
        return jsonify({"status": "sucesso", "mensagem": "Usuário registrado com sucesso!"}), 201

    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({"status": "erro", "mensagem": "Este apelido já está em uso."}), 409
    except Exception as e:
        conn.rollback()
        print(f"Erro no registro: {e}")
        return jsonify({"status": "erro", "mensagem": "Erro interno do servidor"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    apelido = data.get('apelido')
    senha = data.get('senha')

    if not apelido or not senha:
        return jsonify({"status": "erro", "mensagem": "Apelido e senha são obrigatórios"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "erro", "mensagem": "Não foi possível conectar ao banco de dados"}), 500

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        sql_query = """
            SELECT p.id, p.nome, p.senha_hash, a.pontuacao_total
            FROM profiles p
            JOIN alunos a ON p.id = a.id_profile
            WHERE p.apelido = %s;
        """
        cursor.execute(sql_query, (apelido,))
        user = cursor.fetchone()

        # A CORREÇÃO ESTÁ AQUI: Convertemos o hash do banco para bytes ANTES de comparar.
        if user and bcrypt.checkpw(senha.encode('utf-8'), user['senha_hash'].encode('utf-8')):
            # Login bem-sucedido
            aluno_data = {
                "id": str(user['id']),
                "nome": user['nome'],
                "pontuacao_total": user['pontuacao_total']
            }
            return jsonify({"status": "sucesso", "dados_aluno": aluno_data})
        else:
            # Falha no login
            return jsonify({"status": "erro", "mensagem": "Apelido ou senha inválidos"}), 401

    except Exception as e:
        print(f"Erro no login: {e}")
        return jsonify({"status": "erro", "mensagem": "Erro interno do servidor"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
