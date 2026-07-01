from abc import ABC, abstractmethod
from threading import Lock
from typing import Dict, Optional

from Sessions.models import SessaoConversa


class BaseSessionRepository(ABC):
    @abstractmethod
    def obter_sessao_ativa_por_usuario(self, usuario_id: str) -> Optional[SessaoConversa]:
        raise NotImplementedError

    @abstractmethod
    def salvar(self, sessao: SessaoConversa) -> SessaoConversa:
        raise NotImplementedError


class InMemorySessionRepository(BaseSessionRepository):
    def __init__(self):
        self._sessoes_por_usuario: Dict[str, SessaoConversa] = {}
        self._lock = Lock()

    def obter_sessao_ativa_por_usuario(self, usuario_id: str) -> Optional[SessaoConversa]:
        with self._lock:
            sessao = self._sessoes_por_usuario.get(usuario_id)

            if sessao and sessao.ativa:
                return sessao

        return None

    def salvar(self, sessao: SessaoConversa) -> SessaoConversa:
        with self._lock:
            self._sessoes_por_usuario[sessao.usuario_id] = sessao

        return sessao
