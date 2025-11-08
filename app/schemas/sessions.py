from pydantic import BaseModel
from datetime import datetime

class SessionBase(BaseModel):
    device_name: str
    ip_address: str
    user_agent: str

class SessionCreate(SessionBase):
    user_id: int
    session_token: str

class Session(SessionBase):
    id: int
    user_id: int
    created_at: datetime
    last_seen: datetime

    class Config:
        from_attributes = True