import abc


class TimerRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def get_timer(self, timer_id: str) -> dict: ...

    @abc.abstractmethod
    async def create_timer(self, timer: dict) -> dict: ...

    @abc.abstractmethod
    async def purge_timers(self) -> None: ...
