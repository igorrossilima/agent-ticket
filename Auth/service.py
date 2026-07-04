import bcrypt
from sqlalchemy.orm import Session

from Auth.schemas import LoginRequest, RegisterRequest
from Auth.token_service import TokenService
from Shared.constants import USER_ROLES
from Users.models import User
from Users.repository import UserRepository


class AuthServiceError(ValueError):
    pass


class EmailJaCadastradoError(AuthServiceError):
    pass


class CredenciaisInvalidasError(AuthServiceError):
    pass


class RoleInvalidaError(AuthServiceError):
    pass


class AuthService:
    def __init__(self, session: Session, token_service: TokenService | None = None):
        self.session = session
        self.users = UserRepository(session)
        self.token_service = token_service or TokenService()

    def registrar_usuario(self, payload: RegisterRequest) -> User:
        if payload.role not in USER_ROLES:
            raise RoleInvalidaError("Role invalida.")

        if self.users.obter_por_email(payload.email):
            raise EmailJaCadastradoError("E-mail ja cadastrado.")

        return self.users.criar(
            name=payload.name,
            email=payload.email,
            password_hash=gerar_hash_senha(payload.password),
            role=payload.role,
        )

    def autenticar_usuario(self, payload: LoginRequest) -> User:
        user = self.users.obter_por_email(payload.email)

        if not user or not user.is_active:
            raise CredenciaisInvalidasError("E-mail ou senha invalidos.")

        if not verificar_senha(payload.password, user.password_hash):
            raise CredenciaisInvalidasError("E-mail ou senha invalidos.")

        return user

    def criar_token(self, user: User) -> str:
        return self.token_service.criar_access_token(user)


def gerar_hash_senha(password: str) -> str:
    senha_bytes = password.encode("utf-8")
    if len(senha_bytes) > 72:
        raise CredenciaisInvalidasError("A senha nao pode ter mais de 72 bytes.")

    return bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode("utf-8")


def verificar_senha(password: str, password_hash: str) -> bool:
    senha_bytes = password.encode("utf-8")
    if len(senha_bytes) > 72:
        return False

    try:
        return bcrypt.checkpw(senha_bytes, password_hash.encode("utf-8"))
    except ValueError:
        return False
