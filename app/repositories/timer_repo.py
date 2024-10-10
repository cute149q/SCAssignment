import abc

from app.models.timer import TimerTask


class TimerRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def get_timer(self, timer_id: str) -> TimerTask | None:
        ...

    @abc.abstractmethod
    async def delete_timer(self, timer_id: str) -> TimerTask | None:
        ...

    @abc.abstractmethod
    async def create_timer(self, timer: TimerTask) -> None:
        ...

    @abc.abstractmethod
    async def get_scheduled_task_id(self) -> str | None:
        ...

    @abc.abstractmethod
    async def add_executed_task(self, timer: TimerTask) -> None:
        ...

    @abc.abstractmethod
    async def get_executed_task(self, timer_id: str) -> TimerTask | None:
        ...
