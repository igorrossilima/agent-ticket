import hashlib

from Auth.models import UsuarioAutenticado


class TokenInvalidoError(ValueError):
    pass


class TokenService:
    def identificar_usuario(self, token: str) -> UsuarioAutenticado:
        token_limpo = token.strip() if token else ""

        if not token_limpo:
            raise TokenInvalidoError("Token de autenticação inválido.")

        return UsuarioAutenticado(
            usuario_id=self._gerar_usuario_id(token_limpo),
            token=token_limpo,
        )

    @staticmethod
    def _gerar_usuario_id(token: str) -> str:
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        return f"usr_{token_hash[:24]}"
