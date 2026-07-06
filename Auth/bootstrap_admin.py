from Auth.schemas import RegisterRequest
from Auth.service import AuthService
from Users.models import User
from Users.repository import UserRepository


class BootstrapAdminError(ValueError):
    pass


def criar_primeiro_admin(
    *,
    session,
    name: str,
    email: str,
    password: str,
) -> User:
    name = name.strip()
    email = email.strip().lower()
    password = password.strip()

    if not name:
        raise BootstrapAdminError("Nome do admin inicial nao informado.")

    if not email:
        raise BootstrapAdminError("E-mail do admin inicial nao informado.")

    if not password:
        raise BootstrapAdminError("Senha do admin inicial nao informada.")

    if UserRepository(session).contar() > 0:
        raise BootstrapAdminError(
            "Bootstrap de admin permitido apenas quando nao existem usuarios cadastrados."
        )

    return AuthService(session).registrar_usuario(
        RegisterRequest(
            name=name,
            email=email,
            password=password,
            role="admin",
        )
    )
