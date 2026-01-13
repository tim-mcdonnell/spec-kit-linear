---
description: Generate Linear Milestones and Issues from the Plan Issue artifacts. Triggered by `ai:tasks` label in CI or manually.
handoffs:
  - label: Analyze For Consistency
    agent: speckit.analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: speckit.implement
    prompt: Start the implementation in phases
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The input should include the Project identifier.

## Outline

This command reads the Plan Issue and its artifact comments, then creates Milestones and Issues in Linear. In CI mode, this is triggered when the `ai:tasks` label is added to a Project.

### Execution Steps

1. **Load Project and Plan Issue**:

   ```graphql
   query GetProject($id: String!) {
     project(id: $id) {
       id
       name
       identifier
       content
       url
       teams { nodes { id key } }
       projectMilestones { nodes { id name } }
       issues {
         nodes {
           id
           identifier
           title
           description
           state { name }
           comments { nodes { id body createdAt } }
         }
       }
     }
   }
   ```

   - Parse Project ID from input or CI webhook payload
   - Load `linear-config.json` for team/label/state IDs
   - Find the Plan Issue (title starts with "Plan:")
   - Extract all comments from Plan Issue (Research, Data Model, Contracts, etc.)

2. **Verify Plan Issue is complete**:
   - Check Plan Issue state is "Done"
   - If not "Done", error: "Plan Issue must be completed before generating tasks. Run `/speckit.plan` first."
   - Extract spec from Project `content` field
   - Parse artifact comments for:
     - Research findings
     - Data model entities
     - API contracts
     - User stories and priorities

3. **Generate task breakdown**:

   From the spec and Plan Issue artifacts, derive:

   a. **Phases (become Milestones)**:
      - Phase 1: Setup (project initialization)
      - Phase 2: Foundational (blocking prerequisites)
      - Phase 3+: One phase per user story (in priority order)
      - Final Phase: Polish & cross-cutting concerns

   b. **Tasks (become Issues)**:
      - Setup tasks from project structure
      - Data model entities → model creation issues
      - API contracts → endpoint implementation issues
      - User stories → feature implementation issues
      - Each task must be specific enough for an agent to implement

4. **Create Milestones**:

   ```graphql
   mutation CreateMilestone($input: ProjectMilestoneCreateInput!) {
     projectMilestoneCreate(input: $input) {
       projectMilestone { id name }
       success
     }
   }
   ```

   For each phase, create a Milestone with:
   - `projectId`: The project ID
   - `name`: Phase name (e.g., "1. Setup", "2. Foundational", "3. User Authentication")
   - `description`: Phase goals and completion criteria
   - `sortOrder`: Sequential ordering (1.0, 2.0, 3.0, etc.)

5. **Create Issues** (tasks):

   ```graphql
   mutation CreateIssue($input: IssueCreateInput!) {
     issueCreate(input: $input) {
       issue { id identifier title }
       success
     }
   }
   ```

   For each task, create an Issue with:
   - `teamId`: Team ID from config
   - `title`: Task description (with ID prefix like "[T001]")
   - `description`: Detailed task requirements including:
     - What to implement
     - File paths to create/modify
     - Acceptance criteria
     - Dependencies (if any)
   - `projectId`: The project ID
   - `projectMilestoneId`: The appropriate milestone ID
   - `priority`: Based on user story priority (P1 → 1, P2 → 2, etc.)

6. **Create blocking relations**:

   ```graphql
   mutation CreateBlockingRelation($input: IssueRelationCreateInput!) {
     issueRelationCreate(input: $input) {
       issueRelation { id type }
       success
     }
   }
   ```

   - All Phase 2+ issues are blocked by Plan Issue
   - Setup issues block all other issues
   - Foundational issues block user story issues
   - Within a phase, order tasks by logical dependencies

7. **Post summary comment on Plan Issue**:

   ```graphql
   mutation AddComment($input: CommentCreateInput!) {
     commentCreate(input: $input) {
       comment { id body }
       success
     }
   }
   ```

   Include:
   - Total milestones created
   - Total issues created per phase
   - Issue identifiers grouped by milestone
   - Dependency graph summary
   - Next step: "Add `ai:ready` label to issues you want worked"

8. **Handle errors or questions**:

   - **If needs human input**:
     - Post comment with specific questions on Plan Issue
     - Add `ai:needs-input` label to Plan Issue
     - Exit

   - **If successful**:
     - Remove `ai:tasks` label from Project (in CI mode)
     - Exit with success

9. **Report completion**:
   - Number of milestones created
   - Number of issues created
   - Summary by phase
   - Suggested MVP scope (typically Phase 1-3)
   - Instructions for starting implementation

## Task Generation Rules

### Task Format

Each Issue must include:

1. **Title**: `[T###] Action verb + what + where`
   - Example: `[T001] Initialize project structure`
   - Example: `[T005] Create User model in src/models/user.py`

2. **Description** (markdown):
   ```markdown
   ## Objective
   [What this task accomplishes]

   ## Files
   - Create: `src/models/user.py`
   - Modify: `src/models/__init__.py`

   ## Requirements
   - [Specific requirement 1]
   - [Specific requirement 2]

   ## Acceptance Criteria
   - [ ] [Criterion 1]
   - [ ] [Criterion 2]

   ## Dependencies
   - Blocked by: TIM-001, TIM-002
   - Blocks: TIM-010, TIM-011
   ```

3. **Labels**: Add `parallel` label if task can run in parallel with others in same phase

### Phase Structure

- **Phase 1: Setup**
  - Project initialization
  - Dependency installation
  - Configuration files
  - No [Story] label

- **Phase 2: Foundational**
  - Shared infrastructure
  - Base models/types
  - Core utilities
  - No [Story] label

- **Phase 3+: User Stories**
  - One phase per user story from spec
  - Each phase independently testable
  - Include [US#] in issue labels

- **Final Phase: Polish**
  - Documentation
  - Performance optimization
  - Cross-cutting concerns

## CI Mode Behavior

When triggered by `ai:tasks` label on Project via webhook:

1. Parse webhook payload for Project ID
2. Load project, Plan Issue, and artifact comments
3. Verify Plan Issue is complete
4. Generate milestones and issues
5. Create blocking relations
6. Post summary comment
7. Remove `ai:tasks` label from Project
8. Exit with success

## Linear API Reference

### Get Project with Issues
```graphql
query GetProject($id: String!) {
  project(id: $id) {
    id
    name
    identifier
    content
    url
    teams { nodes { id key } }
    projectMilestones { nodes { id name sortOrder } }
    issues {
      nodes {
        id
        identifier
        title
        description
        state { name }
        comments { nodes { id body createdAt } }
      }
    }
  }
}
```

### Create Milestone
```graphql
mutation CreateMilestone($input: ProjectMilestoneCreateInput!) {
  projectMilestoneCreate(input: $input) {
    projectMilestone { id name sortOrder }
    success
  }
}
```

### Create Issue
```graphql
mutation CreateIssue($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    issue { id identifier title }
    success
  }
}
```

### Create Blocking Relation
```graphql
mutation CreateBlockingRelation($input: IssueRelationCreateInput!) {
  issueRelationCreate(input: $input) {
    issueRelation { id type }
    success
  }
}
```

### Add Comment
```graphql
mutation AddComment($input: CommentCreateInput!) {
  commentCreate(input: $input) {
    comment { id body }
    success
  }
}
```

## Key Rules

- Tasks are Linear Issues, not files
- Phases are Linear Milestones
- All blocking relations are explicit via Issue Relations
- Each Issue must be independently executable by an agent
- Include file paths and acceptance criteria in every Issue description
