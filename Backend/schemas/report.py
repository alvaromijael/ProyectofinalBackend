from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReportResponse(BaseModel):
    id: int
    appointment_id: int
    file_path: str
    file_name: str
    file_size_bytes: int
    generated_at: datetime

    class Config:
        from_attributes = True


class ReportGenerateRequest(BaseModel):
    appointment_id: int
    db_host: Optional[str] = "localhost"
    db_port: Optional[str] = "5432"
    db_name: Optional[str] = "femixweb3"
    db_user: Optional[str] = "postgres"
    db_password: Optional[str] = "sa"