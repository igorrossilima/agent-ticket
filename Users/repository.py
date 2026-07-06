from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from Customers import models as customer_models  # noqa: F401
from Tickets import models as ticket_models  # noqa: F401
from Users.models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def criar(
        self,
        *,
        name: str,
        email: str,
        password_hash: str,
        role: str = "agent",
        is_active: bool = True,
    ) -> User:
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)
        return user

    def obter_por_id(self, user_id: UUID) -> User | None:
        return self.session.get(User, user_id)

    def obter_por_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.session.execute(statement).scalar_one_or_none()

    def contar(self) -> int:
        statement = select(func.count()).select_from(User)
        return self.session.execute(statement).scalar_one()
