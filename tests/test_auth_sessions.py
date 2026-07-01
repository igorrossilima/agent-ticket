import unittest

from Auth.token_service import TokenInvalidoError, TokenService
from Sessions.repository import InMemorySessionRepository
from Sessions.service import SessionService


class AuthSessionTest(unittest.TestCase):
    def test_token_service_identifica_usuario_de_forma_estavel(self):
        service = TokenService()

        usuario = service.identificar_usuario("token-abc")
        mesmo_usuario = service.identificar_usuario("token-abc")

        self.assertEqual(usuario.usuario_id, mesmo_usuario.usuario_id)
        self.assertEqual(usuario.token, "token-abc")

    def test_token_service_rejeita_token_vazio(self):
        service = TokenService()

        with self.assertRaises(TokenInvalidoError):
            service.identificar_usuario("   ")

    def test_session_service_obtem_ou_cria_sessao_ativa_por_usuario(self):
        token_service = TokenService()
        session_service = SessionService(repository=InMemorySessionRepository())
        usuario = token_service.identificar_usuario("token-usuario")

        primeira_sessao = session_service.obter_ou_criar_sessao(usuario)
        segunda_sessao = session_service.obter_ou_criar_sessao(usuario)

        self.assertEqual(primeira_sessao.session_id, segunda_sessao.session_id)
        self.assertEqual(primeira_sessao.usuario_id, usuario.usuario_id)
        self.assertTrue(primeira_sessao.ativa)


if __name__ == "__main__":
    unittest.main()
