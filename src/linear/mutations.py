# ABOUTME: GraphQL mutation operations for writing Linear data
# Provides methods to create/update issues, projects, comments, and relations

from typing import Optional

from .client import LinearClient
from .types import (
    Issue,
    Project,
    Milestone,
    Comment,
    IssueRelation,
    IssueRelationType,
    IssuePriority,
)
from .queries import LinearQueries


class LinearMutations:
    """GraphQL mutation operations for Linear API."""

    def __init__(self, client: LinearClient):
        self.client = client
        self._queries = LinearQueries(client)

    # ============ Project Operations ============

    def create_project(
        self,
        name: str,
        team_ids: list[str],
        description: Optional[str] = None,
        content: Optional[str] = None,
        status_id: Optional[str] = None,
    ) -> Project:
        """
        Create a new project.

        Args:
            name: Project name.
            team_ids: List of team UUIDs.
            description: Short description.
            content: Full spec content (markdown).
            status_id: Initial status ID.

        Returns:
            Created Project object.
        """
        mutation = """
        mutation CreateProject($input: ProjectCreateInput!) {
            projectCreate(input: $input) {
                project {
                    id
                    name
                    identifier
                    description
                    content
                    url
                }
                success
            }
        }
        """
        input_data = {
            "name": name,
            "teamIds": team_ids,
        }
        if description:
            input_data["description"] = description
        if content:
            input_data["content"] = content
        if status_id:
            input_data["statusId"] = status_id

        data = self.client.execute(mutation, {"input": input_data})
        proj = data["projectCreate"]["project"]
        return Project(
            id=proj["id"],
            name=proj["name"],
            identifier=proj.get("identifier"),
            description=proj.get("description"),
            content=proj.get("content"),
            url=proj.get("url"),
            team_ids=team_ids,
        )

    def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        content: Optional[str] = None,
        status_id: Optional[str] = None,
    ) -> Project:
        """
        Update a project.

        Args:
            project_id: Project UUID.
            name: New name.
            description: New description.
            content: New content.
            status_id: New status ID.

        Returns:
            Updated Project object.
        """
        mutation = """
        mutation UpdateProject($id: String!, $input: ProjectUpdateInput!) {
            projectUpdate(id: $id, input: $input) {
                project {
                    id
                    name
                    identifier
                    description
                    content
                    url
                    status { id name }
                }
                success
            }
        }
        """
        input_data = {}
        if name is not None:
            input_data["name"] = name
        if description is not None:
            input_data["description"] = description
        if content is not None:
            input_data["content"] = content
        if status_id is not None:
            input_data["statusId"] = status_id

        data = self.client.execute(mutation, {"id": project_id, "input": input_data})
        return self._queries.get_project(project_id)

    # ============ Issue Operations ============

    def create_issue(
        self,
        title: str,
        team_id: str,
        description: Optional[str] = None,
        project_id: Optional[str] = None,
        milestone_id: Optional[str] = None,
        priority: IssuePriority = IssuePriority.NONE,
        label_ids: Optional[list[str]] = None,
        state_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
    ) -> Issue:
        """
        Create a new issue.

        Args:
            title: Issue title.
            team_id: Team UUID.
            description: Issue description (markdown).
            project_id: Project UUID.
            milestone_id: Milestone UUID.
            priority: Priority level.
            label_ids: Label UUIDs.
            state_id: Initial workflow state ID.
            assignee_id: Assignee user ID.

        Returns:
            Created Issue object.
        """
        mutation = """
        mutation CreateIssue($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                issue {
                    id
                    identifier
                    title
                    url
                }
                success
            }
        }
        """
        input_data = {
            "title": title,
            "teamId": team_id,
        }
        if description:
            input_data["description"] = description
        if project_id:
            input_data["projectId"] = project_id
        if milestone_id:
            input_data["projectMilestoneId"] = milestone_id
        if priority != IssuePriority.NONE:
            input_data["priority"] = priority.value
        if label_ids:
            input_data["labelIds"] = label_ids
        if state_id:
            input_data["stateId"] = state_id
        if assignee_id:
            input_data["assigneeId"] = assignee_id

        data = self.client.execute(mutation, {"input": input_data})
        issue_data = data["issueCreate"]["issue"]
        return self._queries.get_issue(issue_data["id"])

    def update_issue(
        self,
        issue_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        state_id: Optional[str] = None,
        priority: Optional[IssuePriority] = None,
        label_ids: Optional[list[str]] = None,
        milestone_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
    ) -> Issue:
        """
        Update an issue.

        Args:
            issue_id: Issue UUID.
            title: New title.
            description: New description.
            state_id: New state ID.
            priority: New priority.
            label_ids: New label IDs (replaces existing).
            milestone_id: New milestone ID.
            assignee_id: New assignee ID.

        Returns:
            Updated Issue object.
        """
        mutation = """
        mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
            issueUpdate(id: $id, input: $input) {
                issue {
                    id
                    identifier
                    title
                    state { id name }
                }
                success
            }
        }
        """
        input_data = {}
        if title is not None:
            input_data["title"] = title
        if description is not None:
            input_data["description"] = description
        if state_id is not None:
            input_data["stateId"] = state_id
        if priority is not None:
            input_data["priority"] = priority.value
        if label_ids is not None:
            input_data["labelIds"] = label_ids
        if milestone_id is not None:
            input_data["projectMilestoneId"] = milestone_id
        if assignee_id is not None:
            input_data["assigneeId"] = assignee_id

        self.client.execute(mutation, {"id": issue_id, "input": input_data})
        return self._queries.get_issue(issue_id)

    def add_issue_label(self, issue_id: str, label_id: str) -> Issue:
        """
        Add a label to an issue.

        Args:
            issue_id: Issue UUID.
            label_id: Label UUID to add.

        Returns:
            Updated Issue object.
        """
        # Get current labels first
        issue = self._queries.get_issue(issue_id)
        current_label_ids = [l.id for l in issue.labels]
        if label_id not in current_label_ids:
            current_label_ids.append(label_id)
        return self.update_issue(issue_id, label_ids=current_label_ids)

    def remove_issue_label(self, issue_id: str, label_id: str) -> Issue:
        """
        Remove a label from an issue.

        Args:
            issue_id: Issue UUID.
            label_id: Label UUID to remove.

        Returns:
            Updated Issue object.
        """
        issue = self._queries.get_issue(issue_id)
        current_label_ids = [l.id for l in issue.labels if l.id != label_id]
        return self.update_issue(issue_id, label_ids=current_label_ids)

    # ============ Comment Operations ============

    def create_comment(self, issue_id: str, body: str) -> Comment:
        """
        Add a comment to an issue.

        Args:
            issue_id: Issue UUID.
            body: Comment body (markdown).

        Returns:
            Created Comment object.
        """
        mutation = """
        mutation CreateComment($input: CommentCreateInput!) {
            commentCreate(input: $input) {
                comment {
                    id
                    body
                    createdAt
                }
                success
            }
        }
        """
        data = self.client.execute(
            mutation, {"input": {"issueId": issue_id, "body": body}}
        )
        comment = data["commentCreate"]["comment"]
        return Comment(
            id=comment["id"],
            body=comment["body"],
            created_at=comment["createdAt"],
        )

    # ============ Milestone Operations ============

    def create_milestone(
        self,
        project_id: str,
        name: str,
        description: Optional[str] = None,
        sort_order: Optional[float] = None,
        target_date: Optional[str] = None,
    ) -> Milestone:
        """
        Create a project milestone.

        Args:
            project_id: Project UUID.
            name: Milestone name.
            description: Milestone description.
            sort_order: Sort order (lower = earlier).
            target_date: Target completion date (ISO format).

        Returns:
            Created Milestone object.
        """
        mutation = """
        mutation CreateMilestone($input: ProjectMilestoneCreateInput!) {
            projectMilestoneCreate(input: $input) {
                projectMilestone {
                    id
                    name
                    description
                    sortOrder
                    targetDate
                }
                success
            }
        }
        """
        input_data = {
            "projectId": project_id,
            "name": name,
        }
        if description:
            input_data["description"] = description
        if sort_order is not None:
            input_data["sortOrder"] = sort_order
        if target_date:
            input_data["targetDate"] = target_date

        data = self.client.execute(mutation, {"input": input_data})
        ms = data["projectMilestoneCreate"]["projectMilestone"]
        return Milestone(
            id=ms["id"],
            name=ms["name"],
            description=ms.get("description"),
            sort_order=ms.get("sortOrder"),
            project_id=project_id,
            target_date=ms.get("targetDate"),
        )

    # ============ Relation Operations ============

    def create_blocking_relation(
        self, blocker_issue_id: str, blocked_issue_id: str
    ) -> IssueRelation:
        """
        Create a blocking relation (blocker blocks blocked).

        Args:
            blocker_issue_id: Issue that blocks.
            blocked_issue_id: Issue that is blocked.

        Returns:
            Created IssueRelation object.
        """
        mutation = """
        mutation CreateBlockingRelation($input: IssueRelationCreateInput!) {
            issueRelationCreate(input: $input) {
                issueRelation {
                    id
                    type
                }
                success
            }
        }
        """
        data = self.client.execute(
            mutation,
            {
                "input": {
                    "issueId": blocker_issue_id,
                    "relatedIssueId": blocked_issue_id,
                    "type": "blocks",
                }
            },
        )
        rel = data["issueRelationCreate"]["issueRelation"]
        return IssueRelation(
            id=rel["id"],
            type=IssueRelationType.BLOCKS,
            issue_id=blocker_issue_id,
            related_issue_id=blocked_issue_id,
        )

    def check_blockers_complete(self, issue_id: str) -> tuple[bool, list[str]]:
        """
        Check if all blocking issues are complete.

        Args:
            issue_id: Issue UUID to check.

        Returns:
            Tuple of (all_complete, list of incomplete blocker identifiers).
        """
        issue = self._queries.get_issue(issue_id)
        incomplete_blockers = []

        for relation in issue.relations:
            if relation.type == IssueRelationType.BLOCKED_BY:
                if relation.related_issue_state and relation.related_issue_state.lower() not in [
                    "done",
                    "completed",
                    "canceled",
                    "cancelled",
                ]:
                    incomplete_blockers.append(
                        relation.related_issue_identifier or relation.related_issue_id
                    )

        return len(incomplete_blockers) == 0, incomplete_blockers

    # ============ Label Operations ============

    def create_label(
        self,
        team_id: str,
        name: str,
        color: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        """
        Create a new label.

        Args:
            team_id: Team UUID.
            name: Label name.
            color: Label color (hex without #).
            description: Label description.

        Returns:
            Created label ID.
        """
        mutation = """
        mutation CreateLabel($input: IssueLabelCreateInput!) {
            issueLabelCreate(input: $input) {
                issueLabel {
                    id
                    name
                }
                success
            }
        }
        """
        input_data = {
            "teamId": team_id,
            "name": name,
        }
        if color:
            input_data["color"] = color
        if description:
            input_data["description"] = description

        data = self.client.execute(mutation, {"input": input_data})
        return data["issueLabelCreate"]["issueLabel"]["id"]

    # ============ Convenience Methods ============

    def create_plan_issue(
        self,
        project: Project,
        team_id: str,
        summary: Optional[str] = None,
    ) -> Issue:
        """
        Create the Plan Issue for a project.

        Args:
            project: Project object.
            team_id: Team UUID.
            summary: Initial plan summary.

        Returns:
            Created Plan Issue.
        """
        title = f"Plan: {project.name}"
        description = summary or f"Implementation plan for {project.name}"
        return self.create_issue(
            title=title,
            team_id=team_id,
            description=description,
            project_id=project.id,
        )

    def post_artifact(
        self,
        issue_id: str,
        artifact_type: str,
        content: str,
    ) -> Comment:
        """
        Post an artifact as a comment on the Plan Issue.

        Args:
            issue_id: Plan Issue UUID.
            artifact_type: Type of artifact (e.g., "Research", "Data Model", "API Contracts").
            content: Artifact content (markdown).

        Returns:
            Created Comment object.
        """
        body = f"## {artifact_type}\n\n{content}"
        return self.create_comment(issue_id, body)
