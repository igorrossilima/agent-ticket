from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from Tickets import models as ticket_models  # noqa: F401
from Customers.models import Customer


class CustomerRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar(
        self,
        *,
        name: str,
        email: str | None = None,
        phone: str | None = None,
        document: str | None = None,
    ) -> Customer:
        customer = Customer(
            name=name,
            email=email,
            phone=phone,
            document=document,
        )
        self.session.add(customer)
        self.session.flush()
        self.session.refresh(customer)
        return customer

    def obter_por_id(self, customer_id: UUID) -> Customer | None:
        return self.session.get(Customer, customer_id)

    def obter_por_email(self, email: str) -> Customer | None:
        statement = select(Customer).where(Customer.email == email).limit(1)
        return self.session.execute(statement).scalar_one_or_none()

    def obter_por_documento(self, document: str) -> Customer | None:
        statement = select(Customer).where(Customer.document == document).limit(1)
        return self.session.execute(statement).scalar_one_or_none()

    def listar(self, *, limit: int = 50, offset: int = 0) -> list[Customer]:
        statement = (
            select(Customer)
            .order_by(Customer.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.execute(statement).scalars().all())

    def atualizar(
        self,
        customer: Customer,
        *,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        document: str | None = None,
    ) -> Customer:
        if name is not None:
            customer.name = name

        customer.email = email
        customer.phone = phone
        customer.document = document

        self.session.flush()
        self.session.refresh(customer)
        return customer
