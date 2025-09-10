import os
import psycopg2
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
    """
    Registra um novo perfil (aluno ou professor).
    Espera um JSON com: nome, apelido, senha, tipo_pessoa ('aluno' ou 'professor')
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('nome', 'apelido', 'senha', 'tipo_pessoa')):
        return jsonify({"status": "erro", "mensagem": "Dados incompletos"}), 400

    nome = data['nome']
    apelido = data['apelido']
    senha = data['senha']
    tipo_pessoa = data['tipo_pessoa']

    # Criptografa a senha antes de salvar (MUITO IMPORTANTE)
    hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "erro", "mensagem": "Falha na conexão com o banco de dados"}), 500

    try:
        with conn.cursor() as cur:
            # Insere na tabela 'profiles'
            cur.execute(
                "INSERT INTO profiles (nome, apelido, senha_hash, tipo_pessoa) VALUES (%s, %s, %s, %s) RETURNING id",
                (nome, apelido, hashed_password.decode('utf-8'), tipo_pessoa)
            )
            profile_id = cur.fetchone()[0]

            # Insere na tabela específica (Alunos ou Professores)
            if tipo_pessoa == 'aluno':
                cur.execute("INSERT INTO Alunos (id_profile) VALUES (%s)", (profile_id,))
            elif tipo_pessoa == 'professor':
                cur.execute("INSERT INTO Professores (id_profile) VALUES (%s)", (profile_id,))

        conn.commit()
        return jsonify({"status": "sucesso", "mensagem": "Usuário registrado com sucesso"}), 201

    except psycopg2.IntegrityError: # Erro ocorre se o apelido já existir
        conn.rollback()
        return jsonify({"status": "erro", "mensagem": "Este apelido já está em uso"}), 409
    except Exception as e:
        conn.rollback()
        print(f"Erro no registro: {e}")
        return jsonify({"status": "erro", "mensagem": "Erro interno do servidor"}), 500
    finally:
        if conn:
            conn.close()


@app.route('/login', methods=['POST'])
def login():
    """
    Realiza o login de um aluno.
    Espera um JSON com: apelido, senha
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('apelido', 'senha')):
        return jsonify({"status": "erro", "mensagem": "Dados incompletos"}), 400
    
    apelido = data['apelido']
    senha = data['senha']

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "erro", "mensagem": "Falha na conexão com o banco de dados"}), 500
        
    try:
        with conn.cursor() as cur:
            # Busca o perfil do aluno e seus dados da tabela Alunos
            cur.execute(
                """
                SELECT p.id, p.nome, p.senha_hash, a.pontuacao_total
                FROM profiles p
                JOIN Alunos a ON p.id = a.id_profile
                WHERE p.apelido = %s AND p.tipo_pessoa = 'aluno'
                """,
                (apelido,)
            )
            user_data = cur.fetchone()

        if user_data:
            user_id, user_nome, user_senha_hash, user_pontuacao = user_data
            
            # Compara a senha enviada com a senha criptografada no banco
            if bcrypt.checkpw(senha.encode('utf-8'), user_senha_hash.encode('utf-8')):
                # Login bem-sucedido
                response_data = {
                    "status": "sucesso",
                    "dados_aluno": {
                        "id": str(user_id), # Converte UUID para string
                        "nome": user_nome,
                        "pontuacao_total": user_pontuacao
                    }
                }
                return jsonify(response_data)

        # Se o usuário não foi encontrado ou a senha está incorreta
        return jsonify({"status": "erro", "mensagem": "Apelido ou senha incorretos"}), 401

    except Exception as e:
        print(f"Erro no login: {e}")
        return jsonify({"status": "erro", "mensagem": "Erro interno do servidor"}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Roda o servidor localmente para testes na porta 5000
    app.run(debug=True, port=5000)

