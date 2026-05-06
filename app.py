from flask import (
    Flask,
    render_template,
    send_from_directory,
    request,
    jsonify,
    redirect,
    url_for,
    session
)
from flask_cors import CORS
from api.indicadores_service import calcular_indicadores_unidade
import index
import sqlite3
import hashlib
import os
import config_rnds  # opcional, para unidade_padrao


# ------------------------------------------------------------------
# CONFIGURAÇÃO BÁSICA DO FLASK
# ------------------------------------------------------------------

# static_folder='.' permite servir arquivos .html da raiz do projeto
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# IMPORTANTE: defina uma secret_key para usar sessão
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "troque-esta-chave-secreta")

DB_PATH = os.path.join(os.path.dirname(__file__), 'pacientes.db')


# ------------------------------------------------------------------
# ROTAS DA PÁGINA DE INDICADORES (HTML) + API RNDS
# ------------------------------------------------------------------

@app.route("/indicadores")
def indicadores():
    """
    Tela HTML de indicadores, visível apenas para usuários
    com perfil 'medico' ou 'enfermeira'.
    """
    perfil = session.get("perfil")  # ajuste o nome da chave conforme seu login

    if perfil not in ["medico", "enfermeira"]:
        # Se não for médico nem enfermeira, volta para tela de login HTML
        return redirect(url_for("login_page"))

    # Exemplo simples (você pode buscar da API abaixo ou do banco):
    indicadores = {
        "hipertensao_total": 145,
        "diabetes_controlados": 89
    }

    # Renderiza templates/indicadores.html
    return render_template("indicadores.html", indicadores=indicadores)


# Rota genérica: recebe qualquer CNES na URL
@app.route("/api/indicadores/unidade/<cnes>")
def indicadores_unidade(cnes):
    """
    Exemplo de chamada:
    GET /api/indicadores/unidade/1234567?inicio=2026-01-01&fim=2026-01-31
    """
    data_inicio = request.args.get("inicio", "2026-01-01")
    data_fim = request.args.get("fim", "2026-01-31")
    indicadores = calcular_indicadores_unidade(cnes, data_inicio, data_fim)
    return jsonify(indicadores)


# (Opcional) rota fixa para testar sempre o mesmo CNES
@app.route("/api/indicadores/unidade_teste")
def indicadores_unidade_teste():
    """
    Exemplo de chamada:
    GET /api/indicadores/unidade_teste?inicio=2026-01-01&fim=2026-01-31
    """
    cnes = "1234567"
    data_inicio = request.args.get("inicio", "2026-01-01")
    data_fim = request.args.get("fim", "2026-01-31")
    indicadores = calcular_indicadores_unidade(cnes, data_inicio, data_fim)
    return jsonify(indicadores)

# (Opcional) se um dia quiser unidade padrão, é só descomentar:
# @app.route("/api/indicadores/unidade_padrao")
# def indicadores_unidade_padrao():
#     cnes = config_rnds.CNES_UNIDADE_PADRAO
#     data_inicio = request.args.get("inicio", "2026-01-01")
#     data_fim = request.args.get("fim", "2026-01-31")
#     indicadores = calcular_indicadores_unidade(cnes, data_inicio, data_fim)
#     return jsonify(indicadores)


# ------------------------------------------------------------------
# ROTAS DO FRONT-END (HTML) - TELAS ESTÁTICAS
# ------------------------------------------------------------------

@app.route('/')
def root():
    # Abre a tela de login na raiz
    return send_from_directory('.', 'login.html')


@app.route('/login.html')
def login_page():
    return send_from_directory('.', 'login.html')


@app.route('/index.html')
def index_page():
    return send_from_directory('.', 'index.html')


@app.route('/paciente.html')
def paciente_page():
    return send_from_directory('.', 'paciente.html')


@app.route('/responsavel.html')
def responsavel_page():
    return send_from_directory('.', 'responsavel.html')


@app.route('/afericao.html')
def afericao_page():
    return send_from_directory('.', 'afericao.html')


@app.route('/medicacao.html')
def medicacao_page():
    return send_from_directory('.', 'medicacao.html')


@app.route('/unidades.html')
def unidades_page():
    return send_from_directory('.', 'unidades.html')


@app.route('/cadastro_paciente.html')
def cadastro_paciente_page():
    return send_from_directory('.', 'cadastro_paciente.html')


@app.route('/cadastro_responsavel.html')
def cadastro_responsavel_page():
    return send_from_directory('.', 'cadastro_responsavel.html')


@app.route('/cadastro_paciente_publico.html')
def cadastro_paciente_publico_page():
    return send_from_directory('.', 'cadastro_paciente_publico.html')


# ------------------------------------------------------------------
# ROTAS DAS PÁGINAS DE PROFISSIONAIS
# ------------------------------------------------------------------

@app.route('/enfermeira.html')
def enfermeira_page():
    return send_from_directory('.', 'enfermeira.html')


@app.route('/fisioterapeuta.html')
def fisioterapeuta_page():
    return send_from_directory('.', 'fisioterapeuta.html')


@app.route('/fono.html')
def fono_page():
    return send_from_directory('.', 'fono.html')


@app.route('/nutricionista.html')
def nutricionista_page():
    return send_from_directory('.', 'nutricionista.html')


@app.route('/odonto.html')
def odonto_page():
    return send_from_directory('.', 'odonto.html')


@app.route('/psicologia.html')
def psicologia_page():
    return send_from_directory('.', 'psicologia.html')


@app.route('/tec_enf.html')
def tec_enf_page():
    return send_from_directory('.', 'tec_enf.html')


@app.route('/tec_geriatria.html')
def tec_geriatria_page():
    return send_from_directory('.', 'tec_geriatria.html')


@app.route('/terapeuta_ocupacional.html')
def terapeuta_ocupacional_page():
    return send_from_directory('.', 'terapeuta_ocupacional.html')


# ------------------------------------------------------------------
# FUNÇÕES DE BANCO / INICIALIZAÇÃO
# ------------------------------------------------------------------

def get_db():
    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id                               INTEGER PRIMARY KEY AUTOINCREMENT,
            nome                             TEXT    NOT NULL,
            data_nascimento                  TEXT    NOT NULL,
            cpf                              TEXT    NOT NULL UNIQUE,
            telefone                         TEXT,
            endereco                         TEXT,
            sexo                             TEXT,
            condicao                         TEXT,
            profissional_responsavel         TEXT,
            profissional_responsavel_nome    TEXT,
            senha_hash                       TEXT,
            criado_em TEXT DEFAULT (datetime('now','localtime'))
        )
    ''')
    try:
        c.execute("ALTER TABLE pacientes ADD COLUMN senha_hash TEXT")
    except Exception:
        pass

    c.execute('''
        CREATE TABLE IF NOT EXISTS medicacoes (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id             INTEGER NOT NULL REFERENCES pacientes(id),
            nome_medicacao          TEXT    NOT NULL,
            posologia               TEXT    NOT NULL,
            forma_farmaceutica      TEXT,
            intervalo_uso           TEXT,
            observacoes             TEXT,
            em_uso                  INTEGER DEFAULT 1,
            criado_em TEXT DEFAULT (datetime('now','localtime'))
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS afericoes (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id             INTEGER REFERENCES pacientes(id),
            data_hora               TEXT,
            pa_sistolica            INTEGER,
            pa_diastolica           INTEGER,
            frequencia_cardiaca     INTEGER,
            temperatura             REAL,
            glicemia                INTEGER,
            saturacao               INTEGER,
            observacoes             TEXT,
            criado_em TEXT DEFAULT (datetime('now','localtime'))
        )
    ''')
    for col, tipo in [
        ('pa_sistolica', 'INTEGER'), ('pa_diastolica', 'INTEGER'),
        ('frequencia_cardiaca', 'INTEGER'), ('temperatura', 'REAL'),
        ('glicemia', 'INTEGER'), ('saturacao', 'INTEGER'),
    ]:
        try:
            c.execute(f"ALTER TABLE afericoes ADD COLUMN {col} {tipo}")
        except Exception:
            pass

    c.execute('''
        CREATE TABLE IF NOT EXISTS responsaveis (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            nome              TEXT    NOT NULL,
            data_nascimento   TEXT,
            cpf               TEXT    UNIQUE,
            email             TEXT    NOT NULL UNIQUE,
            telefone          TEXT,
            tipo_responsavel  TEXT,
            numero_registro   TEXT,
            senha_hash        TEXT    NOT NULL,
            criado_em         TEXT DEFAULT (datetime('now','localtime'))
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS historico_tomada (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicacao_id INTEGER NOT NULL REFERENCES medicacoes(id),
            data_hora_prevista TEXT NOT NULL,
            data_hora_tomada TEXT,
            criado_em TEXT DEFAULT (datetime('now','localtime'))
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS evolucoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL REFERENCES pacientes(id),
            responsavel_id INTEGER,
            nome_paciente TEXT,
            cpf_paciente TEXT,
            texto TEXT NOT NULL,
            meds_em_uso TEXT,
            criado_em TEXT DEFAULT (datetime('now','localtime'))
        )
    ''')

    conn.commit()
    conn.close()


init_db()


# ------------------------------------------------------------------
# PACIENTES (APIs)
# ------------------------------------------------------------------

@app.route('/api/pacientes', methods=['GET'])
def listar_pacientes():
    conn = get_db()
    rows = conn.execute('SELECT * FROM pacientes ORDER BY criado_em DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


@app.route('/api/pacientes', methods=['POST'])
def cadastrar_paciente():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({'erro': 'Corpo da requisição inválido.'}), 400

    faltando = [c for c in ['nome', 'data_nascimento', 'cpf']
                if not str(dados.get(c, '')).strip()]
    if faltando:
        return jsonify({'erro': f'Campos obrigatórios ausentes: {", ".join(faltando)}'}), 400

    cpf_limpo  = dados['cpf'].replace('.', '').replace('-', '').strip()
    senha_raw  = dados.get('senha', cpf_limpo)
    senha_hash = hash_senha(senha_raw)

    conn = get_db()
    try:
        cur = conn.execute('''
            INSERT INTO pacientes
              (nome, data_nascimento, cpf, telefone, endereco, sexo,
               condicao, profissional_responsavel, profissional_responsavel_nome, senha_hash)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        ''', (
            dados['nome'].strip(),
            dados['data_nascimento'].strip(),
            dados['cpf'].strip(),
            dados.get('telefone', '').strip(),
            dados.get('endereco', '').strip(),
            dados.get('sexo', '').strip(),
            dados.get('condicao', '').strip(),
            dados.get('profissional_responsavel', '').strip(),
            dados.get('profissional_responsavel_nome', '').strip(),
            senha_hash,
        ))
        conn.commit()
        novo_id = cur.lastrowid
        return jsonify({
            'mensagem': 'Paciente cadastrado com sucesso!',
            'paciente': {'id': novo_id, 'nome': dados['nome']}
        }), 201
    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({'erro': 'CPF já cadastrado no sistema.'}), 409
    except Exception as e:
        conn.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500
    finally:
        conn.close()


@app.route('/api/pacientes/login', methods=['POST'])
def login_paciente():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({'erro': 'JSON inválido.'}), 400

    cpf   = str(dados.get('cpf', '')).strip()
    senha = str(dados.get('senha', ''))

    if not cpf or not senha:
        return jsonify({'erro': 'Informe CPF e senha.'}), 400

    cpf_limpo = cpf.replace('.', '').replace('-', '')

    conn = get_db()
    row  = conn.execute(
        "SELECT * FROM pacientes WHERE REPLACE(REPLACE(cpf, '.', ''), '-', '') = ?",
        (cpf_limpo,)
    ).fetchone()
    conn.close()

    if not row:
        return jsonify({'erro': 'Paciente não encontrado.'}), 404

    # Senha padrão é o CPF sem pontuação
    senha_hash_cadastrada = row['senha_hash'] or hash_senha(cpf_limpo)
    # Aceita senha digitada com ou sem formatação do CPF
    senha_limpa = senha.replace('.', '').replace('-', '')
    if hash_senha(senha) != senha_hash_cadastrada and hash_senha(senha_limpa) != senha_hash_cadastrada:
        return jsonify({'erro': 'CPF ou senha incorretos.'}), 401

    return jsonify({
        'mensagem': 'Login realizado com sucesso!',
        'paciente': {
            'id':       row['id'],
            'nome':     row['nome'],
            'cpf':      row['cpf'],
            'condicao': row['condicao'],
            'data_nascimento': row['data_nascimento'],
            'telefone': row['telefone'],
            'endereco': row['endereco'],
            'profissional_responsavel': row['profissional_responsavel'],
            'profissional_responsavel_nome': row['profissional_responsavel_nome'],
        }
    }), 200


@app.route('/api/pacientes/<cpf>', methods=['GET'])
def obter_paciente_por_cpf(cpf):
    cpf_limpo = cpf.replace('.', '').replace('-', '').strip()
    conn = get_db()
    row  = conn.execute(
        "SELECT * FROM pacientes WHERE REPLACE(REPLACE(cpf, '.', ''), '-', '') = ?",
        (cpf_limpo,)
    ).fetchone()
    conn.close()
    if not row:
        return jsonify({'erro': 'Paciente não encontrado.'}), 404
    return jsonify(dict(row)), 200


# ------------------------------------------------------------------
# MEDICAÇÕES (APIs)
# ------------------------------------------------------------------

@app.route('/api/pacientes/<int:paciente_id>/medicacoes', methods=['GET'])
def listar_medicacoes(paciente_id):
    conn = get_db()
    pac  = conn.execute('SELECT id FROM pacientes WHERE id=?', (paciente_id,)).fetchone()
    if not pac:
        conn.close()
        return jsonify({'erro': 'Paciente não encontrado.'}), 404
    rows = conn.execute(
        'SELECT * FROM medicacoes WHERE paciente_id=? ORDER BY criado_em DESC',
        (paciente_id,)
    ).fetchall()
    meds = []
    for r in rows:
        med = dict(r)
        # Exemplo: horários previstos fixos
        med['horarios_previstos'] = ['08:00', '20:00']
        # Busca histórico de tomada
        hist = conn.execute(
            'SELECT data_hora_prevista, data_hora_tomada FROM historico_tomada WHERE medicacao_id=? ORDER BY data_hora_prevista DESC LIMIT 30',
            (med['id'],)
        ).fetchall()
        med['historico_tomada'] = [dict(h) for h in hist]
        meds.append(med)
    conn.close()
    return jsonify(meds), 200


@app.route('/api/pacientes/<int:paciente_id>/medicacoes', methods=['POST'])
def criar_medicacao(paciente_id):
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({'erro': 'JSON inválido.'}), 400

    faltando = [c for c in ['nome_medicacao', 'posologia']
                if not str(dados.get(c, '')).strip()]
    if faltando:
        return jsonify({'erro': f'Campos obrigatórios: {", ".join(faltando)}'}), 400

    conn = get_db()
    pac  = conn.execute('SELECT id FROM pacientes WHERE id=?', (paciente_id,)).fetchone()
    if not pac:
        conn.close()
        return jsonify({'erro': 'Paciente não encontrado.'}), 404

    cur = conn.execute('''
        INSERT INTO medicacoes
          (paciente_id, nome_medicacao, posologia, forma_farmaceutica,
           intervalo_uso, observacoes, em_uso)
        VALUES (?,?,?,?,?,?,1)
    ''', (
        paciente_id,
        dados['nome_medicacao'].strip(),
        dados['posologia'].strip(),
        dados.get('forma_farmaceutica', ''),
        dados.get('intervalo_uso', ''),
        dados.get('observacoes', ''),
    ))
    conn.commit()
    novo_id = cur.lastrowid
    row     = conn.execute('SELECT * FROM medicacoes WHERE id=?', (novo_id,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


@app.route('/api/medicacoes/<int:med_id>', methods=['PUT'])
def atualizar_medicacao(med_id):
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({'erro': 'JSON inválido.'}), 400

    conn  = get_db()
    atual = conn.execute('SELECT * FROM medicacoes WHERE id=?', (med_id,)).fetchone()
    if not atual:
        conn.close()
        return jsonify({'erro': 'Medicação não encontrada.'}), 404

    atual = dict(atual)
    conn.execute('''
        UPDATE medicacoes SET
          nome_medicacao=?, posologia=?, forma_farmaceutica=?,
          intervalo_uso=?, observacoes=?, em_uso=?
        WHERE id=?
    ''', (
        dados.get('nome_medicacao',     atual['nome_medicacao']),
        dados.get('posologia',          atual['posologia']),
        dados.get('forma_farmaceutica', atual['forma_farmaceutica']),
        dados.get('intervalo_uso',      atual['intervalo_uso']),
        dados.get('observacoes',        atual['observacoes']),
        int(dados.get('em_uso',         atual['em_uso'])),
        med_id,
    ))
    conn.commit()
    row = conn.execute('SELECT * FROM medicacoes WHERE id=?', (med_id,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 200


@app.route('/api/medicacoes/<int:med_id>/confirmar_tomada', methods=['POST'])
def confirmar_tomada(med_id):
    dados = request.get_json(silent=True)
    data_hora_prevista = dados.get('data_hora_prevista')
    if not data_hora_prevista:
        return jsonify({'erro': 'Data/hora prevista obrigatória.'}), 400
    conn = get_db()
    reg = conn.execute(
        'SELECT * FROM historico_tomada WHERE medicacao_id=? AND data_hora_prevista=?',
        (med_id, data_hora_prevista)
    ).fetchone()
    if reg:
        conn.execute(
            'UPDATE historico_tomada SET data_hora_tomada=datetime("now","localtime") WHERE id=?',
            (reg['id'],)
        )
    else:
        conn.execute(
            'INSERT INTO historico_tomada (medicacao_id, data_hora_prevista, data_hora_tomada) VALUES (?, ?, datetime("now","localtime"))',
            (med_id, data_hora_prevista)
        )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Tomada confirmada!'}), 200


# ------------------------------------------------------------------
# AFERIÇÕES (APIs)
# ------------------------------------------------------------------

@app.route('/api/afericoes', methods=['POST'])
def registrar_afericao():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({'erro': 'JSON inválido.'}), 400

    conn = get_db()
    cur  = conn.execute('''
        INSERT INTO afericoes
          (paciente_id, data_hora, pa_sistolica, pa_diastolica,
           frequencia_cardiaca, temperatura, glicemia, saturacao, observacoes)
        VALUES (?,?,?,?,?,?,?,?,?)
    ''', (
        dados.get('paciente_id'),
        dados.get('data_hora', ''),
        dados.get('pa_sistolica'),
        dados.get('pa_diastolica'),
        dados.get('frequencia_cardiaca'),
        dados.get('temperatura'),
        dados.get('glicemia'),
        dados.get('saturacao'),
        dados.get('observacoes', ''),
    ))
    conn.commit()
    novo_id = cur.lastrowid
    conn.close()
    return jsonify({'mensagem': 'Aferição registrada com sucesso!', 'id': novo_id}), 201


@app.route('/api/afericoes', methods=['GET'])
def listar_afericoes():
    paciente_id = request.args.get('paciente_id')
    conn = get_db()
    if paciente_id:
        rows = conn.execute(
            'SELECT * FROM afericoes WHERE paciente_id=? ORDER BY criado_em DESC',
            (paciente_id,)
        ).fetchall()
    else:
        rows = conn.execute('SELECT * FROM afericoes ORDER BY criado_em DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


# ------------------------------------------------------------------
# RESPONSÁVEIS (APIs)
# ------------------------------------------------------------------

@app.route('/api/responsaveis', methods=['POST'])
def cadastrar_responsavel():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({'erro': 'JSON inválido.'}), 400

    for campo in ['nome', 'email', 'senha']:
        if not str(dados.get(campo, '')).strip():
            return jsonify({'erro': f'Campo obrigatório ausente: {campo}'}), 400

    if len(dados['senha']) < 6:
        return jsonify({'erro': 'A senha deve ter pelo menos 6 caracteres.'}), 400

    conn = get_db()
    try:
        cur = conn.execute('''
            INSERT INTO responsaveis
              (nome, data_nascimento, cpf, email, telefone,
               tipo_responsavel, numero_registro, senha_hash)
            VALUES (?,?,?,?,?,?,?,?)
        ''', (
            dados['nome'].strip(),
            dados.get('data_nascimento', '').strip(),
            dados.get('cpf', '').strip() or None,
            dados['email'].strip().lower(),
            dados.get('telefone', '').strip(),
            dados.get('tipo_responsavel', '').strip(),
            dados.get('numero_registro', '').strip(),
            hash_senha(dados['senha']),
        ))
        conn.commit()
        novo_id = cur.lastrowid
        return jsonify({
            'mensagem': 'Responsável cadastrado com sucesso!',
            'responsavel': {'id': novo_id, 'nome': dados['nome']}
        }), 201
    except sqlite3.IntegrityError as e:
        conn.rollback()
        err = str(e)
        if 'email' in err:
            return jsonify({'erro': 'Este e-mail já está cadastrado.'}), 409
        if 'cpf' in err:
            return jsonify({'erro': 'Este CPF já está cadastrado.'}), 409
        return jsonify({'erro': 'Dado duplicado.'}), 409
    except Exception as e:
        conn.rollback()
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500
    finally:
        conn.close()


@app.route('/api/responsaveis/login', methods=['POST'])
def login_responsavel():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({'erro': 'JSON inválido.'}), 400

    identificador = str(dados.get('identificador', '')).strip().lower()
    senha         = str(dados.get('senha', ''))

    if not identificador or not senha:
        return jsonify({'erro': 'Informe e-mail/CPF e senha.'}), 400

    identificador_limpo = identificador.replace('.', '').replace('-', '')

    conn = get_db()
    row  = conn.execute(
        'SELECT * FROM responsaveis WHERE LOWER(email)=? OR cpf=? OR cpf=?',
        (identificador, identificador, identificador_limpo)
    ).fetchone()
    conn.close()

    if not row:
        return jsonify({'erro': 'Usuário não encontrado.'}), 404
    if row['senha_hash'] != hash_senha(senha):
        return jsonify({'erro': 'Senha incorreta.'}), 401

    return jsonify({
        'mensagem': 'Login realizado com sucesso!',
        'responsavel': {
            'id':               row['id'],
            'nome':             row['nome'],
            'email':            row['email'],
            'tipo_responsavel': row['tipo_responsavel'],
            'tipo':             row['tipo_responsavel'],
        }
    }), 200


@app.route('/api/responsaveis', methods=['GET'])
def listar_responsaveis():
    conn = get_db()
    rows = conn.execute(
        'SELECT id, nome, email, cpf, tipo_responsavel, numero_registro, criado_em '
        'FROM responsaveis ORDER BY criado_em DESC'
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


# ------------------------------------------------------------------
# EVOLUÇÕES (APIs)
# ------------------------------------------------------------------

@app.route('/api/pacientes/<int:paciente_id>/evolucoes', methods=['POST'])
def salvar_evolucao(paciente_id):
    dados = request.get_json(silent=True)
    texto = dados.get('texto', '').strip()
    responsavel_id = dados.get('responsavel_id')
    nome_paciente = dados.get('nome_paciente', '').strip()
    cpf_paciente = dados.get('cpf_paciente', '').strip()
    meds_em_uso = dados.get('meds_em_uso', '')
    if not texto:
        return jsonify({'erro': 'Texto da evolução obrigatório.'}), 400
    conn = get_db()
    conn.execute('''
        INSERT INTO evolucoes (paciente_id, responsavel_id, nome_paciente, cpf_paciente, texto, meds_em_uso)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (paciente_id, responsavel_id, nome_paciente, cpf_paciente, texto, meds_em_uso))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Evolução salva com sucesso!'}), 201


@app.route('/api/pacientes/<int:paciente_id>/evolucoes', methods=['GET'])
def listar_evolucoes(paciente_id):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM evolucoes WHERE paciente_id=? ORDER BY criado_em DESC',
        (paciente_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True, port=5000)