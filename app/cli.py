import click
from sqlmodel import Session, select
from app.database import engine
from app.models import User, UserRole
from app.services.password import hash_password


@click.group()
def cli():
    """쇼핑몰 CLI"""
    pass


@cli.command()
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--name", prompt=True)
def create_admin(email: str, password: str, name: str):
    """관리자 계정 생성"""
    with Session(engine) as session:
        # 중복 확인
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            click.echo(f"이미 존재하는 이메일입니다: {email}")
            return

        # 생성
        admin = User(
            email=email,
            name=name,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN
        )
        session.add(admin)
        session.commit()

        click.echo(f"관리자 계정이 생성되었습니다: {email}")


if __name__ == "__main__":
    cli()
