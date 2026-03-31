from pydantic import BaseModel, Field

class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class UserRolesUpdate(BaseModel):
    role_ids: list[int] = Field(
        min_length=1,
        examples=[[1, 2]],
        description="List of role IDs to assign. Get available IDs from GET /roles"
    )
