from typing import Type, Any, Callable, TypeVar
from fastapi import Request, Depends as FastApiDepends
import functools

T = TypeVar('T')

def ResolveDependency(_type: Type[T]) -> Any:
    def resolver(t: Type[T], request: Request) -> Callable[[], T]:
        return request.app.state.ioc_container.resolve(t)

    return FastApiDepends(functools.partial(resolver, _type))