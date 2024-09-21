from pydantic import BaseModel
from datetime import date


class BorrowEntryModel(BaseModel):
    id: int
    book_id: int
    user_id: int
    date_borrowed: date
    return_date: date
    is_returned: bool = False

    class Config:
        from_attributes = True
