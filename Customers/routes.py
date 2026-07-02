from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from Customers.schemas import CustomerCreate, CustomerRead, CustomerUpdate
from Customers.service import (
    CustomerNaoEncontradoError,
    CustomerService,
    CustomerServiceError,
    ValorCustomerInvalidoError,
)
from Postgres.session import obter_sessao_db


router = APIRouter(prefix="/customers", tags=["customers"])


def obter_customer_service(
    session: Session = Depends(obter_sessao_db),
) -> CustomerService:
    return CustomerService(session)


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def criar_customer(
    payload: CustomerCreate,
    service: CustomerService = Depends(obter_customer_service),
) -> CustomerRead:
    try:
        customer = service.criar_customer(payload)
        service.session.commit()
        service.session.refresh(customer)
        return customer
    except CustomerServiceError as erro:
        service.session.rollback()
        raise _converter_erro_servico(erro) from erro


@router.get("", response_model=list[CustomerRead])
def listar_customers(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: CustomerService = Depends(obter_customer_service),
) -> list[CustomerRead]:
    return service.listar_customers(limit=limit, offset=offset)


@router.get("/by-email/{email}", response_model=CustomerRead)
def obter_customer_por_email(
    email: str,
    service: CustomerService = Depends(obter_customer_service),
) -> CustomerRead:
    try:
        return service.obter_por_email(email)
    except CustomerServiceError as erro:
        raise _converter_erro_servico(erro) from erro


@router.get("/by-document/{document}", response_model=CustomerRead)
def obter_customer_por_documento(
    document: str,
    service: CustomerService = Depends(obter_customer_service),
) -> CustomerRead:
    try:
        return service.obter_por_documento(document)
    except CustomerServiceError as erro:
        raise _converter_erro_servico(erro) from erro


@router.get("/{customer_id}", response_model=CustomerRead)
def obter_customer(
    customer_id: UUID,
    service: CustomerService = Depends(obter_customer_service),
) -> CustomerRead:
    try:
        return service.obter_customer(customer_id)
    except CustomerServiceError as erro:
        raise _converter_erro_servico(erro) from erro


@router.patch("/{customer_id}", response_model=CustomerRead)
def atualizar_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    service: CustomerService = Depends(obter_customer_service),
) -> CustomerRead:
    try:
        customer = service.atualizar_customer(customer_id, payload)
        service.session.commit()
        service.session.refresh(customer)
        return customer
    except CustomerServiceError as erro:
        service.session.rollback()
        raise _converter_erro_servico(erro) from erro


def _converter_erro_servico(erro: CustomerServiceError) -> HTTPException:
    if isinstance(erro, CustomerNaoEncontradoError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro))

    if isinstance(erro, ValorCustomerInvalidoError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro))

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro))
