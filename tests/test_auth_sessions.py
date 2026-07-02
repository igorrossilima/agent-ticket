import unittest
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Auth.token_service import TokenInvalidoError, TokenService
from Postgres.config import obter_config_postgres
from Sessions.repository import InMemorySessionRepository
from Sessions.service import SessionService
from Users.repository import UserRepository


class AuthSessionTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(obter_config_postgres().database_url, pool_pre_ping=True)
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        self.SessionLocal = sessionmaker(
            bind=self.connection,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        self.db_session = self.SessionLocal()

    def tearDown(self):
        self.db_session.close()
        self.transaction.rollback()
        self.connection.close()
        self.engine.dispose()

    def criar_user(self):
        sufixo = uuid4().hex
        return UserRepository(self.db_session).criar(
            name="Usuario Auth Session",
            email=f"auth-session-{sufixo}@example.com",
            password_hash="hash-teste",
        )

    def test_token_service_identifica_usuario_de_forma_estavel(self):
        service = TokenService()
        user = self.criar_user()
        token = service.criar_access_token(user)

        usuario = service.identificar_usuario(token, self.db_session)
        mesmo_usuario = service.identificar_usuario(token, self.db_session)

        self.assertEqual(usuario.usuario_id, mesmo_usuario.usuario_id)
        self.assertEqual(usuario.usuario_id, str(user.id))
        self.assertEqual(usuario.email, user.email)
        self.assertEqual(usuario.token, token)

    def test_token_service_rejeita_token_vazio(self):
        service = TokenService()

        with self.assertRaises(TokenInvalidoError):
            service.identificar_usuario("   ", self.db_session)

    def test_session_service_obtem_ou_cria_sessao_ativa_por_usuario(self):
        token_service = TokenService()
        session_service = SessionService(repository=InMemorySessionRepository())
        user = self.criar_user()
        token = token_service.criar_access_token(user)
        usuario = token_service.identificar_usuario(token, self.db_session)

        primeira_sessao = session_service.obter_ou_criar_sessao(usuario)
        segunda_sessao = session_service.obter_ou_criar_sessao(usuario)

        self.assertEqual(primeira_sessao.session_id, segunda_sessao.session_id)
        self.assertEqual(primeira_sessao.usuario_id, usuario.usuario_id)
        self.assertTrue(primeira_sessao.ativa)


if __name__ == "__main__":
    unittest.main()
