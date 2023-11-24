from neo4j import GraphDatabase

# Configure a conexão com o Neo4j
class Neo4jDriver:
    def __init__(self):
        self._driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "controle"))

    def close(self):
        self._driver.close()

class User:
    def __init__(self, session, nome, idade, localizacao):
        self.session = session
        self.nome = nome
        self.idade = idade
        self.localizacao = localizacao
        self.node_id = None  # Inicialmente, o ID do nó é definido como None

    def create(self):
        query = (
            "CREATE (u:User {nome: $nome, idade: $idade, localizacao: $localizacao})"
            "RETURN ID(u) as node_id"
        )
        result = self.session.run(query, nome=self.nome, idade=self.idade, localizacao=self.localizacao)
        record = result.single()
        self.node_id = record['node_id']  # Atribui o ID do nó retornado à instância da classe

    @classmethod
    def get_by_username(cls, session, username):
        query = (
            "MATCH (u:User {nome: $nome})"
            "RETURN u"
        )
        result = session.run(query, username=username)
        return cls(session, result.single()['u'])

    def __repr__(self):
        return f'<User {self.nome}>'
