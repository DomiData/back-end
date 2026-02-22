from typing import List, Annotated
from fastapi.params import Depends
from fastapi.exceptions import HTTPException
from app.model.role import Role
from app.api.deps import get_current_user
from app.model.user import User


class RoleChecker:
    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Annotated[User, Depends(get_current_user)]):
        for role in user.roles:
            if role in self.allowed_roles:
                return True
        raise HTTPException(
            status_code=403, detail="You do not have permission to access this resource"
        )


allow_admin = RoleChecker([Role.ADMIN])
allow_health_agents = RoleChecker([Role.ADMIN, Role.MANAGER, Role.AGENT])
allow_all = RoleChecker([Role.ADMIN, Role.AGENT, Role.MANAGER, Role.USER])
