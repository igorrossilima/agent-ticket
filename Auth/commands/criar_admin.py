import os
import sys

from Auth.bootstrap_admin import BootstrapAdminError, criar_primeiro_admin
from Postgres.session import SessionLocal


def main() -> int:
    name = os.getenv("BOOTSTRAP_ADMIN_NAME", "")
    email = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "")
    password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")

    session = SessionLocal()

    try:
        user = criar_primeiro_admin(
            session=session,
            name=name,
            email=email,
            password=password,
        )
        session.commit()
        session.refresh(user)
    except BootstrapAdminError as erro:
        session.rollback()
        print(f"Erro ao criar admin inicial: {erro}", file=sys.stderr)
        return 1
    finally:
        session.close()

    print(f"Admin inicial criado: {user.email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
