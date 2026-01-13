# ABOUTME: GraphQL query operations for reading Linear data
# Provides methods to fetch issues, projects, comments, and team config

from typing import Optional

from .client import LinearClient
from .types import (
    Issue,
    Project,
    Milestone,
    Comment,
    Label,
    WorkflowState,
    IssueRelation,
    IssueRelationType,
    IssuePriority,
    Team,
)


class LinearQueries:
    """GraphQL query operations for Linear API."""

    def __init__(self, client: LinearClient):
        self.client = client

    def get_issue(self, issue_id: str) -> Issue:
        """
        Get issue details by ID or identifier (e.g., "TIM-123").

        Args:
            issue_id: Issue UUID or identifier.

        Returns:
            Issue object with full details.
        """
        query = """
        query GetIssue($id: String!) {
            issue(id: $id) {
                id
                identifier
                title
                description
                priority
                url
                branchName
                assignee { id }
                team { id }
                state { id name type color }
                project { id name identifier description content url }
                milestone { id name description sortOrder }
                labels { nodes { id name color description } }
                comments { nodes { id body createdAt updatedAt } }
                relations {
                    nodes {
                        id
                        type
                        relatedIssue {
                            id
                            identifier
                            title
                            state { name }
                        }
                    }
                }
            }
        }
        """
        data = self.client.execute(query, {"id": issue_id})
        return self._parse_issue(data["issue"])

    def get_project(self, project_id: str) -> Project:
        """
        Get project details by ID.

        Args:
            project_id: Project UUID.

        Returns:
            Project object with full details.
        """
        query = """
        query GetProject($id: String!) {
            project(id: $id) {
                id
                name
                identifier
                description
                content
                url
                status { id name }
                teams { nodes { id } }
                projectMilestones { nodes { id name description sortOrder targetDate } }
            }
        }
        """
        data = self.client.execute(query, {"id": project_id})
        return self._parse_project(data["project"])

    def get_issue_comments(self, issue_id: str) -> list[Comment]:
        """
        Get all comments on an issue.

        Args:
            issue_id: Issue UUID or identifier.

        Returns:
            List of Comment objects.
        """
        query = """
        query GetIssueComments($issueId: String!) {
            issue(id: $issueId) {
                comments {
                    nodes {
                        id
                        body
                        createdAt
                        updatedAt
                        user { id }
                    }
                }
            }
        }
        """
        data = self.client.execute(query, {"issueId": issue_id})
        comments_data = data["issue"]["comments"]["nodes"]
        return [
            Comment(
                id=c["id"],
                body=c["body"],
                created_at=c["createdAt"],
                updated_at=c.get("updatedAt"),
                user_id=c.get("user", {}).get("id") if c.get("user") else None,
            )
            for c in comments_data
        ]

    def get_team(self, team_id: str) -> Team:
        """
        Get team details including workflow states and labels.

        Args:
            team_id: Team UUID.

        Returns:
            Team object with states and labels.
        """
        query = """
        query GetTeam($teamId: String!) {
            team(id: $teamId) {
                id
                name
                key
                states { nodes { id name type color position } }
                labels { nodes { id name color description } }
            }
        }
        """
        data = self.client.execute(query, {"teamId": team_id})
        team_data = data["team"]
        return Team(
            id=team_data["id"],
            name=team_data["name"],
            key=team_data["key"],
            states=[
                WorkflowState(
                    id=s["id"],
                    name=s["name"],
                    type=s["type"],
                    color=s.get("color"),
                    position=s.get("position"),
                )
                for s in team_data["states"]["nodes"]
            ],
            labels=[
                Label(
                    id=l["id"],
                    name=l["name"],
                    color=l.get("color"),
                    description=l.get("description"),
                )
                for l in team_data["labels"]["nodes"]
            ],
        )

    def get_project_issues(self, project_id: str) -> list[Issue]:
        """
        Get all issues in a project.

        Args:
            project_id: Project UUID.

        Returns:
            List of Issue objects.
        """
        query = """
        query GetProjectIssues($projectId: String!) {
            project(id: $projectId) {
                issues {
                    nodes {
                        id
                        identifier
                        title
                        description
                        priority
                        url
                        state { id name type }
                        milestone { id name }
                        labels { nodes { id name } }
                    }
                }
            }
        }
        """
        data = self.client.execute(query, {"projectId": project_id})
        issues_data = data["project"]["issues"]["nodes"]
        return [self._parse_issue(i) for i in issues_data]

    def find_plan_issue(self, project_id: str) -> Optional[Issue]:
        """
        Find the Plan Issue for a project (title starts with "Plan:").

        Args:
            project_id: Project UUID.

        Returns:
            Plan Issue if found, None otherwise.
        """
        issues = self.get_project_issues(project_id)
        for issue in issues:
            if issue.title.startswith("Plan:"):
                # Get full issue details
                return self.get_issue(issue.id)
        return None

    def search_issues(
        self,
        query_text: Optional[str] = None,
        team_id: Optional[str] = None,
        project_id: Optional[str] = None,
        label_ids: Optional[list[str]] = None,
        state_ids: Optional[list[str]] = None,
    ) -> list[Issue]:
        """
        Search for issues with filters.

        Args:
            query_text: Text search query.
            team_id: Filter by team.
            project_id: Filter by project.
            label_ids: Filter by labels.
            state_ids: Filter by states.

        Returns:
            List of matching Issue objects.
        """
        # Build filter object
        filter_parts = []
        if team_id:
            filter_parts.append(f'team: {{ id: {{ eq: "{team_id}" }} }}')
        if project_id:
            filter_parts.append(f'project: {{ id: {{ eq: "{project_id}" }} }}')
        if label_ids:
            label_filter = ", ".join([f'"{lid}"' for lid in label_ids])
            filter_parts.append(f"labels: {{ id: {{ in: [{label_filter}] }} }}")
        if state_ids:
            state_filter = ", ".join([f'"{sid}"' for sid in state_ids])
            filter_parts.append(f"state: {{ id: {{ in: [{state_filter}] }} }}")

        filter_str = ", ".join(filter_parts) if filter_parts else ""
        filter_arg = f", filter: {{ {filter_str} }}" if filter_str else ""

        query = f"""
        query SearchIssues($query: String) {{
            issueSearch(query: $query{filter_arg}) {{
                nodes {{
                    id
                    identifier
                    title
                    description
                    priority
                    url
                    state {{ id name type }}
                    project {{ id name }}
                    labels {{ nodes {{ id name }} }}
                }}
            }}
        }}
        """
        variables = {"query": query_text} if query_text else {}
        data = self.client.execute(query, variables)
        return [self._parse_issue(i) for i in data["issueSearch"]["nodes"]]

    def _parse_issue(self, data: dict) -> Issue:
        """Parse issue data from API response."""
        state = None
        if data.get("state"):
            state = WorkflowState(
                id=data["state"]["id"],
                name=data["state"]["name"],
                type=data["state"].get("type", ""),
                color=data["state"].get("color"),
            )

        project = None
        if data.get("project"):
            project = Project(
                id=data["project"]["id"],
                name=data["project"]["name"],
                identifier=data["project"].get("identifier"),
                description=data["project"].get("description"),
                content=data["project"].get("content"),
                url=data["project"].get("url"),
            )

        milestone = None
        if data.get("milestone"):
            milestone = Milestone(
                id=data["milestone"]["id"],
                name=data["milestone"]["name"],
                description=data["milestone"].get("description"),
                sort_order=data["milestone"].get("sortOrder"),
            )

        labels = []
        if data.get("labels", {}).get("nodes"):
            labels = [
                Label(
                    id=l["id"],
                    name=l["name"],
                    color=l.get("color"),
                    description=l.get("description"),
                )
                for l in data["labels"]["nodes"]
            ]

        comments = []
        if data.get("comments", {}).get("nodes"):
            comments = [
                Comment(
                    id=c["id"],
                    body=c["body"],
                    created_at=c["createdAt"],
                    updated_at=c.get("updatedAt"),
                )
                for c in data["comments"]["nodes"]
            ]

        relations = []
        if data.get("relations", {}).get("nodes"):
            for r in data["relations"]["nodes"]:
                rel_issue = r.get("relatedIssue", {})
                relations.append(
                    IssueRelation(
                        id=r["id"],
                        type=IssueRelationType(r["type"].lower()),
                        issue_id=data["id"],
                        related_issue_id=rel_issue.get("id", ""),
                        related_issue_identifier=rel_issue.get("identifier"),
                        related_issue_title=rel_issue.get("title"),
                        related_issue_state=rel_issue.get("state", {}).get("name"),
                    )
                )

        priority_val = data.get("priority", 0) or 0
        priority = IssuePriority(priority_val) if priority_val in range(5) else IssuePriority.NONE

        return Issue(
            id=data["id"],
            identifier=data["identifier"],
            title=data["title"],
            description=data.get("description"),
            priority=priority,
            state=state,
            project=project,
            milestone=milestone,
            labels=labels,
            comments=comments,
            relations=relations,
            branch_name=data.get("branchName"),
            url=data.get("url"),
            assignee_id=data.get("assignee", {}).get("id") if data.get("assignee") else None,
            team_id=data.get("team", {}).get("id") if data.get("team") else None,
        )

    def _parse_project(self, data: dict) -> Project:
        """Parse project data from API response."""
        milestones = []
        if data.get("projectMilestones", {}).get("nodes"):
            milestones = [
                Milestone(
                    id=m["id"],
                    name=m["name"],
                    description=m.get("description"),
                    sort_order=m.get("sortOrder"),
                    target_date=m.get("targetDate"),
                )
                for m in data["projectMilestones"]["nodes"]
            ]

        team_ids = []
        if data.get("teams", {}).get("nodes"):
            team_ids = [t["id"] for t in data["teams"]["nodes"]]

        status_id = None
        status_name = None
        if data.get("status"):
            status_id = data["status"]["id"]
            status_name = data["status"]["name"]

        return Project(
            id=data["id"],
            name=data["name"],
            identifier=data.get("identifier"),
            description=data.get("description"),
            content=data.get("content"),
            url=data.get("url"),
            status_id=status_id,
            status_name=status_name,
            team_ids=team_ids,
            milestones=milestones,
        )
