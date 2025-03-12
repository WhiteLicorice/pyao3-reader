from __future__  import annotations
from typing import Optional

from AO3 import User, utils, Work
import logging

def get_authors(work: Work) -> list[str]:
    authors: list[User] = work.authors
    return [author.username for author in authors]

def resolve_to_work(work: str | int | Work) -> Optional[Work]:
    if isinstance(work, Work):
        return work
    if isinstance(work, str):
        work_id: int = utils.workid_from_url(work)
        return Work(work_id)
    if isinstance(work, int):
        return Work(work)
    else:
        logging.warn(f"Cannot resolve {work} to work!")
        return None