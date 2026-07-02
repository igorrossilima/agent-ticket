from datetime import datetime, timedelta, timezone
from functools import lru_cache
from uuid import UUID

import jwt
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.orm import Session

from Auth.models import UsuarioAutenticado
from Users.models import User
from Users.repository import UserRepository


class TokenInvalidoError(ValueError):
    pass


class TokenSettings(BaseSettings):
    jwt_secret_key: str = "dev-secret-change-me-minimum-32-bytes"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def obter_token_settings() -> TokenSettings:
    return TokenSettings()


class TokenService:
    def __init__(self, settings: TokenSettings | None = None):
        self.settings = settings or obter_token_settings()

    def criar_access_token(self, user: User) -> str:
        agora = datetime.now(timezone.utc)
        expira_em = agora + timedelta(minutes=self.settings.jwt_access_token_expire_minutes)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "iat": agora,
            "exp": expira_em,
        }

        return jwt.encode(
            payload,
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm,
        )

    def identificar_usuario(self, token: str, session: Session) -> UsuarioAutenticado:
        token_limpo = token.strip() if token else ""

        if not token_limpo:
            raise TokenInvalidoError("Token de autenticação inválido.")

        payload = self._decodificar_token(token_limpo)
        usuario_id = payload.get("sub")

        if not usuario_id:
            raise TokenInvalidoError("Token de autenticação inválido.")

        try:
            usuario_uuid = UUID(str(usuario_id))
        except ValueError as erro:
            raise TokenInvalidoError("Token de autenticação inválido.") from erro

        user = UserRepository(session).obter_por_id(usuario_uuid)

        if not user or not user.is_active:
            raise TokenInvalidoError("Usuario autenticado nao encontrado ou inativo.")

        return UsuarioAutenticado(
            usuario_id=str(user.id),
            token=token_limpo,
            email=user.email,
            name=user.name,
            role=user.role,
        )

    def _decodificar_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm],
            )
        except jwt.ExpiredSignatureError as erro:
            raise TokenInvalidoError("Token de autenticação expirado.") from erro
        except jwt.InvalidTokenError as erro:
            raise TokenInvalidoError("Token de autenticação inválido.") from erro
