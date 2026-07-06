from uuid import UUID

from sqlalchemy.orm import Session

from Customers.models import Customer
from Customers.repository import CustomerRepository
from Customers.schemas import CustomerCreate, CustomerUpdate


class CustomerServiceError(ValueError):
    pass


class CustomerNaoEncontradoError(CustomerServiceError):
    pass


class ValorCustomerInvalidoError(CustomerServiceError):
    pass


class CustomerService:
    def __init__(self, session: Session):
        self.session = session
        self.customers = CustomerRepository(session)

    def criar_customer(self, payload: CustomerCreate) -> Customer:
        return self.customers.criar(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            document=payload.document,
            external_contact_id=payload.external_contact_id,
            external_channel=payload.external_channel,
        )

    def obter_customer(self, customer_id: UUID) -> Customer:
        customer = self.customers.obter_por_id(customer_id)

        if not customer:
            raise CustomerNaoEncontradoError("Cliente nao encontrado.")

        return customer

    def obter_por_email(self, email: str) -> Customer:
        email = email.strip()

        if not email:
            raise ValorCustomerInvalidoError("Email do cliente nao pode ser vazio.")

        customer = self.customers.obter_por_email(email)

        if not customer:
            raise CustomerNaoEncontradoError("Cliente nao encontrado.")

        return customer

    def obter_por_documento(self, document: str) -> Customer:
        document = document.strip()

        if not document:
            raise ValorCustomerInvalidoError("Documento do cliente nao pode ser vazio.")

        customer = self.customers.obter_por_documento(document)

        if not customer:
            raise CustomerNaoEncontradoError("Cliente nao encontrado.")

        return customer

    def listar_customers(self, *, limit: int = 50, offset: int = 0) -> list[Customer]:
        return self.customers.listar(limit=limit, offset=offset)

    def atualizar_customer(self, customer_id: UUID, payload: CustomerUpdate) -> Customer:
        customer = self.obter_customer(customer_id)
        campos = payload.model_dump(exclude_unset=True)

        if not campos:
            return customer

        return self.customers.atualizar(
            customer,
            name=campos.get("name", customer.name),
            email=campos.get("email", customer.email),
            phone=campos.get("phone", customer.phone),
            document=campos.get("document", customer.document),
            external_contact_id=campos.get("external_contact_id", customer.external_contact_id),
            external_channel=campos.get("external_channel", customer.external_channel),
        )
