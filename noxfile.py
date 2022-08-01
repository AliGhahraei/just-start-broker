from nox import Session
from nox_poetry import session as nox_session


@nox_session  # type: ignore[misc]
def coverage(session: Session) -> None:
    session.install("coverage[toml]", "pytest")
    session.poetry.installroot()
    try:
        session.run("coverage", "run")
    finally:
        session.run("coverage", "report")


@nox_session  # type: ignore[misc]
def formatting(session: Session) -> None:
    session.install("ufmt")
    session.run("ufmt", "check")


@nox_session  # type: ignore[misc]
def lint(session: Session) -> None:
    session.install("flake8")
    session.run("flake8", "just_start_broker", "tests")


@nox_session  # type: ignore[misc]
def typing(session: Session) -> None:
    session.install("mypy", "pytest")
    session.poetry.installroot(extras=["types"])
    session.run("mypy")
