# main.py
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from db import get_connection

# =========================================================
# Criação da app FastAPI
# =========================================================

app = FastAPI(title="API Doenças Crônicas")

# Middleware de CORS – necessário para permitir acesso dos arquivos HTML locais
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # em desenvolvimento, libera tudo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# Schemas Pydantic
# =========================================================

class PacienteCreate(BaseModel):
    documento: str
    nome: str
    data_nascimento: Optional[str] = None  # formato "YYYY-MM-DD"
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    sexo: Optional[str] = None
    condicao: Optional[str] = None

class Paciente(BaseModel):
    id: int
    documento: str
    nome: str
    data_nascimento: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    sexo: Optional[str] = None
    condicao: Optional[str] = None


class MedicacaoBase(BaseModel):
    nome_medicacao: str
    posologia: str
    forma_farmaceutica: Optional[str] = None
    intervalo_uso: Optional[str] = None
    observacoes: Optional[str] = None
    em_uso: Optional[bool] = True

class MedicacaoCreate(MedicacaoBase):
    pass

class MedicacaoUpdate(BaseModel):
    nome_medicacao: Optional[str] = None
    posologia: Optional[str] = None
    forma_farmaceutica: Optional[str] = None
    intervalo_uso: Optional[str] = None
    observacoes: Optional[str] = None
    em_uso: Optional[bool] = None

class Medicacao(MedicacaoBase):
    id: int
    paciente_id: int
    responsavel_id: Optional[int] = None


# =========================================================
# Endpoints de Pacientes
# =========================================================

@app.post("/pacientes", response_model=Paciente)
def criar_paciente(paciente: PacienteCreate):
    """
    Cria um novo paciente no banco.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO pacientes
                      (documento, nome, data_nascimento, telefone, endereco, sexo, condicao)
                    VALUES
                      (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, documento, nome, data_nascimento, telefone, endereco, sexo, condicao;
                    """,
                    (
                        paciente.documento,
                        paciente.nome,
                        paciente.data_nascimento,
                        paciente.telefone,
                        paciente.endereco,
                        paciente.sexo,
                        paciente.condicao,
                    ),
                )
                row = cur.fetchone()
                return row
    except Exception as e:
        # Exemplo: documento duplicado, erro de constraint etc.
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


@app.get("/pacientes", response_model=List[Paciente])
def listar_pacientes():
    """
    Lista todos os pacientes.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, documento, nome, data_nascimento, telefone, endereco, sexo, condicao
                    FROM pacientes
                    ORDER BY nome;
                    """
                )
                rows = cur.fetchall()
                return rows
    finally:
        conn.close()


@app.get("/pacientes/{documento}", response_model=Paciente)
def obter_paciente_por_documento(documento: str):
    """
    Obtém um paciente filtrando pelo documento (ex: CPF).
    Esse endpoint é usado pelo cadastro de medicações para buscar o paciente pelo CPF.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, documento, nome, data_nascimento, telefone, endereco, sexo, condicao
                    FROM pacientes
                    WHERE documento = %s;
                    """,
                    (documento,),
                )
                row = cur.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="Paciente não encontrado")
                return row
    finally:
        conn.close()


# =========================================================
# Endpoints de Medicações
# =========================================================

@app.get("/pacientes/{paciente_id}/medicacoes", response_model=List[Medicacao])
def listar_medicacoes_paciente(paciente_id: int):
    """
    Lista todas as medicações (em uso ou não) de um paciente.
    Esse endpoint é usado pelo medicacao.html.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Verifica se o paciente existe
                cur.execute("SELECT id FROM pacientes WHERE id = %s;", (paciente_id,))
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="Paciente não encontrado")

                cur.execute(
                    """
                    SELECT
                      id,
                      paciente_id,
                      responsavel_id,
                      nome_medicacao,
                      posologia,
                      forma_farmaceutica,
                      intervalo_uso,
                      observacoes,
                      em_uso
                    FROM medicacoes
                    WHERE paciente_id = %s
                    ORDER BY criado_em DESC;
                    """,
                    (paciente_id,),
                )
                rows = cur.fetchall()
                return rows
    finally:
        conn.close()


@app.post("/pacientes/{paciente_id}/medicacoes", response_model=Medicacao)
def criar_medicacao_para_paciente(paciente_id: int, med: MedicacaoCreate):
    """
    Cadastra uma nova medicação para um paciente.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Verifica se o paciente existe
                cur.execute("SELECT id FROM pacientes WHERE id = %s;", (paciente_id,))
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="Paciente não encontrado")

                cur.execute(
                    """
                    INSERT INTO medicacoes (
                      paciente_id,
                      responsavel_id,
                      nome_medicacao,
                      posologia,
                      forma_farmaceutica,
                      intervalo_uso,
                      observacoes,
                      em_uso
                    ) VALUES (
                      %s, NULL, %s, %s, %s, %s, %s, %s
                    )
                    RETURNING
                      id,
                      paciente_id,
                      responsavel_id,
                      nome_medicacao,
                      posologia,
                      forma_farmaceutica,
                      intervalo_uso,
                      observacoes,
                      em_uso;
                    """,
                    (
                        paciente_id,
                        med.nome_medicacao,
                        med.posologia,
                        med.forma_farmaceutica,
                        med.intervalo_uso,
                        med.observacoes,
                        med.em_uso,
                    ),
                )
                row = cur.fetchone()
                return row
    finally:
        conn.close()


@app.put("/medicacoes/{med_id}", response_model=Medicacao)
def atualizar_medicacao(med_id: int, med: MedicacaoUpdate):
    """
    Atualiza uma medicação existente.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Buscar medicação atual
                cur.execute(
                    """
                    SELECT
                      id,
                      paciente_id,
                      responsavel_id,
                      nome_medicacao,
                      posologia,
                      forma_farmaceutica,
                      intervalo_uso,
                      observacoes,
                      em_uso
                    FROM medicacoes
                    WHERE id = %s;
                    """,
                    (med_id,),
                )
                atual = cur.fetchone()
                if not atual:
                    raise HTTPException(status_code=404, detail="Medicação não encontrada")

                dados_atualizados = {
                    "nome_medicacao": med.nome_medicacao if med.nome_medicacao is not None else atual["nome_medicacao"],
                    "posologia": med.posologia if med.posologia is not None else atual["posologia"],
                    "forma_farmaceutica": med.forma_farmaceutica if med.forma_farmaceutica is not None else atual["forma_farmaceutica"],
                    "intervalo_uso": med.intervalo_uso if med.intervalo_uso is not None else atual["intervalo_uso"],
                    "observacoes": med.observacoes if med.observacoes is not None else atual["observacoes"],
                    "em_uso": med.em_uso if med.em_uso is not None else atual["em_uso"],
                }

                cur.execute(
                    """
                    UPDATE medicacoes
                    SET
                      nome_medicacao = %s,
                      posologia = %s,
                      forma_farmaceutica = %s,
                      intervalo_uso = %s,
                      observacoes = %s,
                      em_uso = %s,
                      atualizado_em = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING
                      id,
                      paciente_id,
                      responsavel_id,
                      nome_medicacao,
                      posologia,
                      forma_farmaceutica,
                      intervalo_uso,
                      observacoes,
                      em_uso;
                    """,
                    (
                        dados_atualizados["nome_medicacao"],
                        dados_atualizados["posologia"],
                        dados_atualizados["forma_farmaceutica"],
                        dados_atualizados["intervalo_uso"],
                        dados_atualizados["observacoes"],
                        dados_atualizados["em_uso"],
                        med_id,
                    ),
                )
                row = cur.fetchone()
                return row
    finally:
        conn.close()