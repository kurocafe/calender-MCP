from pydantic import BaseModel

class DeleteRequest(BaseModel):
  event_id: str