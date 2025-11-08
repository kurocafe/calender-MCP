from pydantic import BaseModel
from typing import Optional

class CreateEventRequest(BaseModel):
  summary: str
  description: Optional[str] = None
  start: str
  end: str
  location: Optional[str] = None