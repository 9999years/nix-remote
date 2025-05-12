import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterator

from loguru import logger


class BackoffTimeout(Exception):
    pass


@dataclass
class Backoff:
    """Exponential backoff configuration."""

    initial_delay: timedelta = timedelta(milliseconds=100)
    max_delay: timedelta = timedelta(seconds=5)
    max_time: timedelta = timedelta(seconds=60)
    factor: float = 1.2

    def __iter__(self) -> Iterator[None]:
        yield

        start_time = datetime.now()
        end_time = start_time + self.max_time

        delay = self.initial_delay

        while datetime.now() <= end_time:
            yield

            delay *= self.factor
            delay = min(delay, self.max_delay)

            elapsed = datetime.now() - start_time

            logger.trace(f"Retrying in {delay}, {elapsed} elapsed")

            time.sleep(delay.total_seconds())

        logger.debug(f"Max time exceeded: {self.max_time}")
        raise BackoffTimeout("Max timeout exceeded")
