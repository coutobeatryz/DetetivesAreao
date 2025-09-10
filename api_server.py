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

        # --- NOVOS REGISTOS DE DEPURAÇÃO ---
        if user:
            print(f"--- INÍCIO DA DEPURAÇÃO DO LOGIN PARA: {apelido} ---")
            
            senha_recebida_da_unity = senha.encode('utf-8')
            senha_hash_do_banco = user['senha_hash'].encode('utf-8')
            
            print(f"Hash do banco de dados: {senha_hash_do_banco}")
            
            # Vamos verificar a palavra-passe e guardar o resultado
            is_password_correct = bcrypt.checkpw(senha_recebida_da_unity, senha_hash_do_banco)
            
            print(f"A palavra-passe está correta? {is_password_correct}")
            print(f"--- FIM DA DEPURAÇÃO ---")

            if is_password_correct:
                # Login bem-sucedido
                aluno_data = {
                    "id": str(user['id']),
                    "nome": user['nome'],
                    "pontuacao_total": user['pontuacao_total']
                }
                return jsonify({"status": "sucesso", "dados_aluno": aluno_data})
        
        # Se o utilizador não for encontrado ou a palavra-passe estiver incorreta
        print(f"Falha no login para o apelido: {apelido}. Utilizador encontrado: {'Sim' if user else 'Não'}")
        return jsonify({"status": "erro", "mensagem": "Apelido ou senha inválidos"}), 401

    except Exception as e:
        print(f"Erro no login: {e}")
        return jsonify({"status": "erro", "mensagem": "Erro interno do servidor"}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
```

### O Que Fazer Agora (O Plano)

1.  **Atualize o Código:** Copie todo o conteúdo do Canvas e cole-o no seu ficheiro `api_server.py`.
2.  **Envie para o GitHub:** Faça o "commit" e "push" da alteração para o seu repositório.
3.  **Aguarde o Deploy:** O Render vai detetar a mudança e iniciar um novo deploy automaticamente. Espere até que ele mostre "Your service is live".
4.  **Teste na Unity:** Tente fazer o login novamente com "bia" e "123456". O erro 401 vai continuar a aparecer na Unity.
5.  **A Pista Final:** Vá para a aba **"Logs"** no Render. Agora, você verá um novo bloco de texto que se parece com isto:

    ```
    --- INÍCIO DA DEPURAÇÃO DO LOGIN PARA: bia ---
    Hash do banco de dados: b'$2b$12$Eflg3jJ3F1vQ3r8yY7p2yO2d.Q5z.1J6z3m.1Z0y8w.9W6u8q7G9y'
    A palavra-passe está correta? False
    --- FIM DA DEPURAÇÃO ---
    Falha no login para o apelido: bia. Utilizador encontrado: Sim
    

