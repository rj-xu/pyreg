from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Callable, Self, final

from .endian import Endian
from .log import logger
from .mask import BitMask
from .reg import Reg


@dataclass
class FieldProperty(BitMask, ABC):
    name: str = field(init=False)
    instance: Reg = field(init=False)

    def __call__(self, _func: Callable[[], Any]):
        # TODO: remove this feature?
        return self

    def __set_name__(self, owner: type, name: str):
        self.name = name

    @abstractmethod
    def __get__(self, instance: Reg, owner: type) -> Any:
        logger.trace(f"Read {self.name}")
        val = instance.read(self)
        return val

    @abstractmethod
    def __set__(self, instance: Reg, val: Any) -> None:
        logger.trace(f"Write {self.name}")
        instance.modify(val, self)

    def check_instance(self, instance: Reg) -> Reg:
        if instance is None:
            logger.error("DO NOT use this field as a class attribute")
            raise AttributeError
        return instance


@dataclass
class BitField(FieldProperty):
    endian: Endian = Endian.LITTLE

    def __get__(self, instance: Reg, owner: type) -> int:
        val = super().__get__(instance, owner)
        if self.endian.is_big:
            # TODO: warning for u16 or remove?
            self.endian.int_to_int(val)
        return val

    def __set__(self, instance: Reg, val: int):
        super().__set__(instance, val)


@dataclass
class TrgProperty(FieldProperty, ABC):
    instance: Reg = field(init=False)

    @final
    def __get__(self, instance: Reg, owner: type) -> Self:
        if not hasattr(self, "instance"):
            self.instance = instance
        return self

    @final
    def __set__(self, instance: Reg, val: int):
        raise NotImplementedError

    @abstractmethod
    def trigger(self, val: Any) -> None: ...


@dataclass
class BitTrigger(TrgProperty):
    val: int = 1

    def trigger(self, val: int | None = None):
        val = val or self.val
        logger.trace(f"Trigger {self.name}")
        self.instance.modify(val, self)
        self.instance.modify(0, self)


@dataclass
class BitEnum[T: IntEnum](FieldProperty):
    def __get__(self, instance: Reg, owner: type) -> T:
        val = super().__get__(instance, owner)
        enum_type: type[T] = self.__orig_class__.__args__[0]  # type: ignore
        return enum_type(val)

    def __set__(self, instance: Reg, val: T):
        super().__set__(instance, val.value)


@dataclass
class BitRsvd(FieldProperty):
    def __get__(self, instance: Reg, owner: type):
        raise NotImplementedError

    def __set__(self, instance: Reg, val: Any):
        raise NotImplementedError


@dataclass
class BitBool(FieldProperty):
    def __init__(self, b: int, base: int = 0):
        super().__init__(b, base=base)

    def __get__(self, instance: Reg, owner: type) -> bool:
        return bool(super().__get__(instance, owner))

    def __set__(self, instance: Reg, val: bool):
        super().__set__(instance, 1 if val else 0)
