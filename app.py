from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "banco.db"

app = Flask(__name__)
CORS(app)


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def adicionar_coluna_se_nao_existir(cursor, tabela, coluna, definicao):
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = [row[1] for row in cursor.fetchall()]
    if coluna not in colunas:
        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")


def criar_tabelas():
    with conectar() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                interesse TEXT NOT NULL,
                email TEXT,
                cidade TEXT,
                estado TEXT,
                tipo_producao TEXT,
                tamanho_propriedade REAL,
                experiencia TEXT,
                foto TEXT,
                bio TEXT,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migração: permite usar um banco antigo sem apagar dados.
        adicionar_coluna_se_nao_existir(cursor, "usuarios", "email", "TEXT")
        adicionar_coluna_se_nao_existir(cursor, "usuarios", "cidade", "TEXT")
        adicionar_coluna_se_nao_existir(cursor, "usuarios", "estado", "TEXT")
        adicionar_coluna_se_nao_existir(cursor, "usuarios", "tipo_producao", "TEXT")
        adicionar_coluna_se_nao_existir(cursor, "usuarios", "tamanho_propriedade", "REAL")
        adicionar_coluna_se_nao_existir(cursor, "usuarios", "experiencia", "TEXT")
        adicionar_coluna_se_nao_existir(cursor, "usuarios", "foto", "TEXT")
        adicionar_coluna_se_nao_existir(cursor, "usuarios", "bio", "TEXT")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comentarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tutorial TEXT NOT NULL,
                nome TEXT NOT NULL,
                texto TEXT NOT NULL,
                data TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simulacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cultura TEXT NOT NULL,
                area REAL NOT NULL,
                clima TEXT NOT NULL,
                sementes REAL NOT NULL,
                agua REAL NOT NULL,
                tempo INTEGER NOT NULL,
                data TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                status TEXT DEFAULT 'nova',
                data TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()


def usuario_para_dict(row):
    if row is None:
        return None
    return dict(row)


@app.route("/", methods=["GET"])
def inicio():
    return jsonify({"mensagem": "API Hungreless funcionando!"})


@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios ORDER BY id DESC")
        usuarios = [usuario_para_dict(row) for row in cursor.fetchall()]
    return jsonify(usuarios)


@app.route("/usuarios/<int:usuario_id>", methods=["GET"])
def buscar_usuario(usuario_id):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        usuario = usuario_para_dict(cursor.fetchone())

    if not usuario:
        return jsonify({"erro": "Usuário não encontrado."}), 404

    return jsonify(usuario)


@app.route("/usuarios", methods=["POST"])
def salvar_usuario():
    dados = request.get_json() or {}
    nome = (dados.get("nome") or "").strip()
    interesse = (dados.get("interesse") or "").strip()

    if not nome or not interesse:
        return jsonify({"erro": "Nome e interesse são obrigatórios."}), 400

    campos = {
        "nome": nome,
        "interesse": interesse,
        "email": (dados.get("email") or "").strip(),
        "cidade": (dados.get("cidade") or "").strip(),
        "estado": (dados.get("estado") or "").strip(),
        "tipo_producao": (dados.get("tipo_producao") or "").strip(),
        "tamanho_propriedade": dados.get("tamanho_propriedade") or None,
        "experiencia": (dados.get("experiencia") or "").strip(),
        "foto": (dados.get("foto") or "").strip(),
        "bio": (dados.get("bio") or "").strip(),
    }

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuarios
            (nome, interesse, email, cidade, estado, tipo_producao, tamanho_propriedade, experiencia, foto, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            campos["nome"], campos["interesse"], campos["email"], campos["cidade"],
            campos["estado"], campos["tipo_producao"], campos["tamanho_propriedade"],
            campos["experiencia"], campos["foto"], campos["bio"]
        ))
        conn.commit()
        usuario_id = cursor.lastrowid
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        usuario = usuario_para_dict(cursor.fetchone())

    return jsonify(usuario)


@app.route("/usuarios/<int:usuario_id>", methods=["PUT"])
def atualizar_usuario(usuario_id):
    dados = request.get_json() or {}
    nome = (dados.get("nome") or "").strip()
    interesse = (dados.get("interesse") or "").strip()

    if not nome or not interesse:
        return jsonify({"erro": "Nome e interesse são obrigatórios."}), 400

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios SET
                nome = ?,
                interesse = ?,
                email = ?,
                cidade = ?,
                estado = ?,
                tipo_producao = ?,
                tamanho_propriedade = ?,
                experiencia = ?,
                foto = ?,
                bio = ?
            WHERE id = ?
        """, (
            nome,
            interesse,
            (dados.get("email") or "").strip(),
            (dados.get("cidade") or "").strip(),
            (dados.get("estado") or "").strip(),
            (dados.get("tipo_producao") or "").strip(),
            dados.get("tamanho_propriedade") or None,
            (dados.get("experiencia") or "").strip(),
            (dados.get("foto") or "").strip(),
            (dados.get("bio") or "").strip(),
            usuario_id
        ))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"erro": "Usuário não encontrado."}), 404

        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        usuario = usuario_para_dict(cursor.fetchone())

    return jsonify(usuario)


@app.route("/comentarios", methods=["GET"])
def listar_comentarios():
    tutorial = request.args.get("tutorial")

    with conectar() as conn:
        cursor = conn.cursor()
        if tutorial:
            cursor.execute(
                "SELECT id, tutorial, nome, texto, data FROM comentarios WHERE tutorial = ? ORDER BY id DESC",
                (tutorial,)
            )
        else:
            cursor.execute("SELECT id, tutorial, nome, texto, data FROM comentarios ORDER BY id DESC")

        comentarios = [dict(row) for row in cursor.fetchall()]

    return jsonify(comentarios)


@app.route("/comentarios", methods=["POST"])
def salvar_comentario():
    dados = request.get_json() or {}
    tutorial = (dados.get("tutorial") or "").strip()
    nome = (dados.get("nome") or "").strip()
    texto = (dados.get("texto") or "").strip()

    if not tutorial or not nome or not texto:
        return jsonify({"erro": "Tutorial, nome e comentário são obrigatórios."}), 400

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO comentarios (tutorial, nome, texto) VALUES (?, ?, ?)",
            (tutorial, nome, texto)
        )
        conn.commit()
        comentario_id = cursor.lastrowid

    return jsonify({"id": comentario_id, "tutorial": tutorial, "nome": nome, "texto": texto})


@app.route("/comentarios/<int:comentario_id>", methods=["DELETE"])
def deletar_comentario(comentario_id):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM comentarios WHERE id = ?", (comentario_id,))
        conn.commit()

    return jsonify({"mensagem": "Comentário excluído."})


@app.route("/simulacoes", methods=["GET"])
def listar_simulacoes():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM simulacoes ORDER BY id DESC LIMIT 50")
        simulacoes = [dict(row) for row in cursor.fetchall()]

    return jsonify(simulacoes)


@app.route("/simulacoes", methods=["POST"])
def salvar_simulacao():
    dados = request.get_json() or {}
    campos = ["cultura", "area", "clima", "sementes", "agua", "tempo"]

    if any(campo not in dados for campo in campos):
        return jsonify({"erro": "Dados incompletos da simulação."}), 400

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO simulacoes (cultura, area, clima, sementes, agua, tempo)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            dados["cultura"], dados["area"], dados["clima"],
            dados["sementes"], dados["agua"], dados["tempo"]
        ))
        conn.commit()
        simulacao_id = cursor.lastrowid

    return jsonify({"id": simulacao_id, "mensagem": "Simulação salva com sucesso."})


@app.route("/mensagens", methods=["GET"])
def listar_mensagens():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mensagens ORDER BY id DESC")
        mensagens = [dict(row) for row in cursor.fetchall()]

    return jsonify(mensagens)


@app.route("/mensagens", methods=["POST"])
def salvar_mensagem():
    dados = request.get_json() or {}
    nome = (dados.get("nome") or "").strip()
    email = (dados.get("email") or "").strip()
    mensagem = (dados.get("mensagem") or "").strip()

    if not nome or not email or not mensagem:
        return jsonify({"erro": "Nome, e-mail e mensagem são obrigatórios."}), 400

    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mensagens (nome, email, mensagem) VALUES (?, ?, ?)",
            (nome, email, mensagem)
        )
        conn.commit()
        mensagem_id = cursor.lastrowid

    return jsonify({"id": mensagem_id, "mensagem": "Mensagem enviada com sucesso!"})


if __name__ == "__main__":
    criar_tabelas()
    app.run(debug=True)
else:
    criar_tabelas()
