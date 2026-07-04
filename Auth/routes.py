from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from Auth.models import UsuarioAutenticado
from Auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserRead
from Auth.service import (
    AuthService,
    AuthServiceError,
    CredenciaisInvalidasError,
    EmailJaCadastradoError,
    RoleInvalidaError,
)
from Auth.token_service import TokenInvalidoError, TokenService
from Postgres.session import obter_sessao_db
from Users.models import User


router = APIRouter(prefix="/auth", tags=["auth"])


def obter_auth_service(
    session: Session = Depends(obter_sessao_db),
) -> AuthService:
    return AuthService(session)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def registrar(
    payload: RegisterRequest,
    service: AuthService = Depends(obter_auth_service),
) -> TokenResponse:
    try:
        user = service.registrar_usuario(payload)
        access_token = service.criar_token(user)
        service.session.commit()
        service.session.refresh(user)
        return TokenResponse(access_token=access_token, user=user)
    except AuthServiceError as erro:
        service.session.rollback()
        raise _converter_erro_auth(erro) from erro


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    service: AuthService = Depends(obter_auth_service),
) -> TokenResponse:
    try:
        user = service.autenticar_usuario(payload)
        access_token = service.criar_token(user)
        return TokenResponse(access_token=access_token, user=user)
    except AuthServiceError as erro:
        raise _converter_erro_auth(erro) from erro


def _obter_usuario_auth_router(
    authorization: str | None = Header(default=None),
    session: Session = Depends(obter_sessao_db),
) -> UsuarioAutenticado:
    token = _extrair_token_bearer(authorization)

    try:
        return TokenService().identificar_usuario(token, session)
    except TokenInvalidoError as erro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(erro),
            headers={"WWW-Authenticate": "Bearer"},
        ) from erro


def _extrair_token_bearer(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não informado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    esquema, separador, token = authorization.partition(" ")

    if separador != " " or esquema.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header Authorization deve usar o formato Bearer <token>.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


@router.get("/me", response_model=UserRead)
def me(
    usuario: UsuarioAutenticado = Depends(_obter_usuario_auth_router),
    session: Session = Depends(obter_sessao_db),
) -> UserRead:
    user = session.get(User, UUID(usuario.usuario_id))

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado.")

    return user


def _converter_erro_auth(erro: AuthServiceError) -> HTTPException:
    if isinstance(erro, EmailJaCadastradoError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro))

    if isinstance(erro, CredenciaisInvalidasError):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(erro))

    if isinstance(erro, RoleInvalidaError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro))

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro))
