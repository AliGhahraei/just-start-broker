import os
from glob import glob
from typing import Any, Iterator

from doit.tools import Interactive, LongRunning, title_with_actions

DOIT_CONFIG = {"default_tasks": ["format"]}


def task_format() -> Iterator[dict[str, Any]]:
    """Format and sort imports for python files."""
    for filepath in glob("**/*.py", recursive=True):
        yield {
            "name": filepath,
            "file_dep": [filepath],
            "actions": [_get_action("ufmt format %(dependencies)s")],
        }


def task_check() -> dict[str, Any]:
    """Run every project check used in CI."""
    return _get_interactive_task("nox")


def task_bump() -> dict[str, Any]:
    """Bump versions in pyproject.toml and poetry.lock ignoring version constraints."""
    return _get_interactive_task("poetryup")


def task_serve() -> dict[str, Any]:
    """Run development server."""
    return {
        "actions": [
            LongRunning(_get_action("uvicorn just_start_broker.app:app --reload"))
        ],
        "title": title_with_actions,
    }


def _get_action(command: str) -> str:
    return f"poetry run {command}"


def _get_interactive_task(action: str) -> dict[str, Any]:
    return {
        "actions": [Interactive(_get_action(action))],
        "title": title_with_actions,
    }
