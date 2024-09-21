from pydantic import BaseModel


class BorrowDetailsModel(BaseModel):
    user_id: int
    borrow_duration_days: int
