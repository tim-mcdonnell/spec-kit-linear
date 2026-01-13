# ABOUTME: Linear API client package for spec-kit integration
# Provides GraphQL client, queries, mutations, and type definitions

from .client import LinearClient
from .types import (
    Issue,
    Project,
    Milestone,
    Comment,
    Label,
    WorkflowState,
    IssueRelation,
    Team,
)
from .queries import LinearQueries
from .mutations import LinearMutations

__all__ = [
    "LinearClient",
    "LinearQueries",
    "LinearMutations",
    "Issue",
    "Project",
    "Milestone",
    "Comment",
    "Label",
    "WorkflowState",
    "IssueRelation",
    "Team",
]
