from abc import ABC, abstractmethod


class BaseEntity(ABC):
    """Common abstract interface for all DevTrack domain entities."""

    @abstractmethod
    def validate(self):
        """Raise ValueError when the entity contains invalid data."""
        raise NotImplementedError

    def to_dict(self):
        """Return the entity's instance attributes as a JSON-friendly mapping."""
        return {
            key: value
            for key, value in self.__dict__.items()
        }


class Reporter(BaseEntity):
    """A person who files engineering issues."""

    def __init__(self, id, name, email, team):
        self.id = id
        self.name = name
        self.email = email
        self.team = team

    def validate(self):
        if not self.name or not str(self.name).strip():
            raise ValueError("Name cannot be empty")
        if "@" not in str(self.email):
            raise ValueError("Invalid email")


class Issue(BaseEntity):
    """A bug report or task filed by a Reporter."""

    ALLOWED_STATUSES = {"open", "in_progress", "resolved", "closed"}
    ALLOWED_PRIORITIES = {"low", "medium", "high", "critical"}

    def __init__(
        self,
        id,
        title,
        description,
        status,
        priority,
        reporter_id,
        created_at=None,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.reporter_id = reporter_id
        if created_at is not None:
            self.created_at = created_at

    def validate(self):
        if not self.title or not str(self.title).strip():
            raise ValueError("Title cannot be empty")
        if self.status not in self.ALLOWED_STATUSES:
            allowed = ", ".join(sorted(self.ALLOWED_STATUSES))
            raise ValueError(f"Status must be one of: {allowed}")
        if self.priority not in self.ALLOWED_PRIORITIES:
            allowed = ", ".join(sorted(self.ALLOWED_PRIORITIES))
            raise ValueError(f"Priority must be one of: {allowed}")

    def describe(self):
        return f"{self.title} [{self.priority}]"


class CriticalIssue(Issue):
    """An Issue whose description emphasizes immediate attention."""

    def describe(self):
        return f"[URGENT] {self.title} — needs immediate attention"


class LowPriorityIssue(Issue):
    """An Issue that can be handled after higher-priority work."""

    def describe(self):
        return f"{self.title} — low priority, handle when free"


__all__ = [
    "BaseEntity",
    "Reporter",
    "Issue",
    "CriticalIssue",
    "LowPriorityIssue",
]
