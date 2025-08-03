from pydantic import BaseModel


class AuthUser(BaseModel):
    email: str
    password: str


class NewUser(BaseModel):
    email: str
    hashed_password: str


class CurrentUser(NewUser):
    id: str
    email: str
    hashed_password: str
    session_id: str = None


class SessionData(BaseModel):
    user_id: str
    last_used_at: float


class SessionResponse(BaseModel):
    session_id: str
