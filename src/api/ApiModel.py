from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional

class ApiResponse(BaseModel):
    success: bool
    messagecode: int = 0
    message: str
    data: Optional[Dict[str, Any]] = {}

    def toJsonResponse(self, status_code: int = 200):
        return JSONResponse(
            status_code=status_code,
            content={
                "success": self.success,
                "messagecode": self.messagecode,
                "message": self.message,
                "data": self.data
            }
        )