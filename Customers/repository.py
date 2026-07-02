from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

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
        statement = select(Customer).where(Customer.email == email)
        return self.session.execute(statement).scalar_one_or_none()

    def obter_por_documento(self, document: str) -> Customer | None:
        statement = select(Customer).where(Customer.document == document)
        return self.session.execute(statement).scalar_one_or_none()
