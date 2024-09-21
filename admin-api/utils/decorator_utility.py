from typing import Callable

from fastapi import HTTPException, status

from utils.custom_exceptions import ConflictException, NotFoundException
from utils.logger_utility import getlogger


def async_controller_exception_handler(controller_func: Callable) -> Callable:
    async def handle_exception(*args, **kwargs):
        logger = getlogger(__name__)
        try:
            return await controller_func(*args, **kwargs)
        except NotFoundException as e:
            logger.info(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ConflictException as e:
            logger.info(e)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An Internal Server Error Occured",
            )

    return handle_exception


def controller_exception_handler(controller_func: Callable) -> Callable:
    def handle_exception(*args, **kwargs):
        logger = getlogger(__name__)
        try:
            return controller_func(*args, **kwargs)
        except NotFoundException as e:
            logger.info(e)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ConflictException as e:
            logger.info(e)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An Internal Server Error Occured",
            )

    return handle_exception
