from uuid import uuid4

from Auth.models import UsuarioAutenticado
from Sessions.models import SessaoConversa, agora_utc
from Sessions.repository import BaseSessionRepository


class SessionService:
    def __init__(self, repository: BaseSessionRepository):
        self.repository = repository

    # passo 9
    def obter_ou_criar_sessao(self, usuario: UsuarioAutenticado) -> SessaoConversa:
        sessao = self.repository.obter_sessao_ativa_por_usuario(usuario.usuario_id)

        if sessao:
            sessao.atualizada_em = agora_utc()
            return self.repository.salvar(sessao)

        nova_sessao = SessaoConversa(
            session_id=str(uuid4()),
            usuario_id=usuario.usuario_id,
        )

        return self.repository.salvar(nova_sessao)
