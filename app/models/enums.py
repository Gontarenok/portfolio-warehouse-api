import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    viewer = "viewer"


class MovementType(str, enum.Enum):
    in_ = "in"
    out = "out"
    transfer = "transfer"
