import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProposalResponse(BaseModel):
    """Schema for returning proposal details."""
    id: uuid.UUID
    user_a_id: uuid.UUID
    user_b_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
