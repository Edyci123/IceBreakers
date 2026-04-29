"""
Meeting-related enumerations.
"""

import enum


class ProposalStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class MeetingSource(str, enum.Enum):
    USER = "user"
    ENGINE = "engine"


class MeetingType(str, enum.Enum):
    COFFEEBREAK = "coffeebreak"
    OTHER = "other"
