from datetime import datetime
from typing import Annotated,Optional
from pydantic import BaseModel,Field,ConfigDict,EmailStr

class SubscriptionCreate(BaseModel):
    email:EmailStr

class SubscriptionResponse(BaseModel):
    id:int
    email:EmailStr
    is_active:bool = True
    created_at:datetime

    model_config=ConfigDict(from_attributes=True)