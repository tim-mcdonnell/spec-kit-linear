# ABOUTME: Type definitions for Linear API objects
# Uses dataclasses for structured data with optional fields

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class IssueRelationType(Enum):
    """Types of relationships between issues."""
    BLOCKS = "blocks"
    BLOCKED_BY = "blocked_by"
    RELATED = "related"
    DUPLICATE = "duplicate"


class IssuePriority(Enum):
    """Issue priority levels (0 = no priority, 1 = urgent, 4 = low)."""
    NONE = 0
    URGENT = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class WorkflowState:
    """Represents a workflow state in Linear."""
    id: str
    name: str
    type: str  # "backlog", "unstarted", "started", "completed", "canceled"
    color: Optional[str] = None
    position: Optional[float] = None


@dataclass
class Label:
    """Represents a label in Linear."""
    id: str
    name: str
    color: Optional[str] = None
    description: Optional[str] = None


@dataclass
class Team:
    """Represents a team in Linear."""
    id: str
    name: str
    key: str
    states: list[WorkflowState] = field(default_factory=list)
    labels: list[Label] = field(default_factory=list)


@dataclass
class Comment:
    """Represents a comment on an issue."""
    id: str
    body: str
    created_at: str
    updated_at: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class IssueRelation:
    """Represents a relationship between issues."""
    id: str
    type: IssueRelationType
    issue_id: str
    related_issue_id: str
    related_issue_identifier: Optional[str] = None
    related_issue_title: Optional[str] = None
    related_issue_state: Optional[str] = None


@dataclass
class Milestone:
    """Represents a project milestone."""
    id: str
    name: str
    description: Optional[str] = None
    sort_order: Optional[float] = None
    project_id: Optional[str] = None
    target_date: Optional[str] = None


@dataclass
class Project:
    """Represents a Linear project."""
    id: str
    name: str
    identifier: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None  # Full spec content stored here
    url: Optional[str] = None
    status_id: Optional[str] = None
    status_name: Optional[str] = None
    team_ids: list[str] = field(default_factory=list)
    milestones: list[Milestone] = field(default_factory=list)


@dataclass
class Issue:
    """Represents a Linear issue."""
    id: str
    identifier: str  # e.g., "TIM-123"
    title: str
    description: Optional[str] = None
    priority: IssuePriority = IssuePriority.NONE
    state: Optional[WorkflowState] = None
    project: Optional[Project] = None
    milestone: Optional[Milestone] = None
    labels: list[Label] = field(default_factory=list)
    comments: list[Comment] = field(default_factory=list)
    relations: list[IssueRelation] = field(default_factory=list)
    branch_name: Optional[str] = None
    url: Optional[str] = None
    assignee_id: Optional[str] = None
    team_id: Optional[str] = None


@dataclass
class ProjectStatus:
    """Represents a project status."""
    id: str
    name: str
    color: Optional[str] = None
    position: Optional[float] = None


@dataclass
class LinearConfig:
    """Configuration for Linear integration."""
    team_id: str
    labels: dict[str, str]  # label name -> label ID
    states: dict[str, str]  # state name -> state ID
    project_statuses: dict[str, str]  # status name -> status ID

    @classmethod
    def from_dict(cls, data: dict) -> "LinearConfig":
        """Create config from dictionary."""
        return cls(
            team_id=data.get("teamId", ""),
            labels=data.get("labels", {}),
            states=data.get("states", {}),
            project_statuses=data.get("projectStatuses", {}),
        )
