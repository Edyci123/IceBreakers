"""
User role enumeration.
Maps to the RBAC table in the architecture document (§3.4).
"""

import enum


class UserRole(str, enum.Enum):
    EMPLOYEE = "employee"
    ADMIN = "admin"
    MANAGER_HR = "manager_hr"
