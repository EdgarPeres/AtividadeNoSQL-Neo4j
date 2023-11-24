from app import app
from flask import request, redirect, url_for
from flask import render_template
from .models import Neo4jDriver, User

# Configure a conexão com o Neo4j
neo4j_driver = Neo4jDriver()


@app.route('/')
def index():
    with neo4j_driver._driver.session() as session:
        # Ajuste na consulta para retornar os atributos específicos
        result = session.run(
            "MATCH (u:User) RETURN ID(u) AS id, u.nome AS nome, u.idade AS idade, u.localizacao AS localizacao")
        usuarios = [
            {"id": record["id"], "nome": record["nome"], "idade": record["idade"], "localizacao": record["localizacao"]}
            for record in result]
        print(usuarios)
    return render_template('index.html', usuarios=usuarios)


@app.route('/novoUsuario')
def novoUsuario():
    return render_template('novoUsuario.html')


@app.route('/salvar_usuario', methods=['POST'])
def salvar_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        idade = request.form['idade']
        localizacao = request.form['localizacao']

        with neo4j_driver._driver.session() as session:
            user = User(session, nome, idade, localizacao)
            user.create()

        # Redirecionar o usuário para a tela inicial após salvar com sucesso
        return redirect(url_for('index'))


@app.route('/usuario/<int:id>')
def detalhes_usuario(id):
    with neo4j_driver._driver.session() as session:
        user_details = session.run(
            "MATCH (u:User) WHERE ID(u) = $id RETURN ID(u) AS id, u.nome AS nome, u.idade AS idade, u.localizacao AS localizacao",
            id=id
        ).single()
        if not user_details:
            return "Usuário não encontrado", 404

        # Convertendo o objeto Record em um dicionário
        usuario = {"id": user_details["id"], "nome": user_details["nome"], "idade": user_details["idade"], "localizacao": user_details["localizacao"]}

        amigos = session.run(
            "MATCH (user:User)-[:FRIEND]->(friend:User) WHERE ID(user) = $id "
            "RETURN ID(friend) AS id, friend.nome AS nome, friend.idade AS idade, friend.localizacao AS localizacao",
            id=id
        ).data()

        nao_amigos = session.run(
            "MATCH (user:User) WHERE ID(user) = $id "
            "MATCH (other:User) WHERE NOT (user)-[:FRIEND]-(other) AND ID(other) <> $id "
            "RETURN ID(other) AS id, other.nome AS nome, other.idade AS idade, other.localizacao AS localizacao",
            id=id
        ).data()

    return render_template(
        'detalhes_usuario.html',
        usuario=usuario,
        amigos=amigos,
        nao_amigos=nao_amigos
    )

@app.route('/adicionar_amizade', methods=['POST'])
def adicionar_amizade():
    user_id = request.form['user_id']
    friend_id = request.form['friend_id']
    with neo4j_driver._driver.session() as session:
        session.run(
            "MATCH (user:User), (other:User) WHERE ID(user) = $user_id AND ID(other) = $friend_id "
            "MERGE (user)-[:FRIEND]->(other)",
            user_id=int(user_id), friend_id=int(friend_id)
        )
    return redirect(url_for('detalhes_usuario', id=user_id))


@app.route('/remover_amizade', methods=['POST'])
def remover_amizade():
    user_id = request.form['user_id']
    friend_id = request.form['friend_id']
    with neo4j_driver._driver.session() as session:
        session.run(
            "MATCH (user:User)-[r:FRIEND]->(friend:User) WHERE ID(user) = $user_id AND ID(friend) = $friend_id "
            "DELETE r",
            user_id=int(user_id), friend_id=int(friend_id)
        )
    return redirect(url_for('detalhes_usuario', id=user_id))

