---
description: Create a Plan Issue for the Linear Project and post planning artifacts as comments. Triggered by `ai:plan` label in CI or manually.
handoffs:
  - label: Create Tasks
    agent: speckit.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: speckit.checklist
    prompt: Create a checklist for the following domain...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The input should include the Project identifier and optionally the tech stack.

## Outline

This command creates the "Plan Issue" for a Linear Project and generates planning artifacts. In CI mode, this is triggered when the `ai:plan` label is added to a Project.

### Execution Steps

1. **Load the Project and configuration**:

   ```graphql
   query GetProject($id: String!) {
     project(id: $id) {
       id
       name
       identifier
       content
       description
       url
       teams { nodes { id key } }
     }
   }
   ```

   - Parse Project ID from user input or CI webhook payload
   - Load `linear-config.json` for team/label/state IDs
   - Verify `LINEAR_TOKEN` is set

2. **Check for existing Plan Issue**:

   ```graphql
   query GetProjectIssues($projectId: String!) {
     project(id: $projectId) {
       issues {
         nodes {
           id
           identifier
           title
           state { name }
         }
       }
     }
   }
   ```

   - Search for issue with title starting with "Plan:"
   - If Plan Issue exists and is not "Done":
     - Resume planning on that issue (add new comments)
   - If Plan Issue exists and is "Done":
     - Create a new "Plan: [Project Name] v2" issue

3. **Create the Plan Issue** (if not exists):

   ```graphql
   mutation CreateIssue($input: IssueCreateInput!) {
     issueCreate(input: $input) {
       issue { id identifier title url }
       success
     }
   }
   ```

   Input:
   - `teamId`: Team ID from config
   - `title`: "Plan: [Project Name]"
   - `description`: Brief summary of planning status
   - `projectId`: The project ID

4. **Execute planning workflow**:

   a. **Technical Context** (extract from user input `{ARGS}`):
      - Parse tech stack mentioned (frameworks, languages, databases)
      - Identify integration points
      - Note any constraints mentioned
      - Mark unknowns as "NEEDS CLARIFICATION"

   b. **Constitution Check**:
      - Load `/memory/constitution.md` if exists
      - Evaluate project against constitution principles
      - Document any gate violations or justifications

   c. **Phase 0: Research** - Generate and post as comment:

      ```graphql
      mutation AddComment($input: CommentCreateInput!) {
        commentCreate(input: $input) {
          comment { id body }
          success
        }
      }
      ```

      Post comment with header `## Research Findings`:
      - For each NEEDS CLARIFICATION → research task
      - For each technology choice → best practices research
      - Consolidate findings with format:
        - Decision: [what was chosen]
        - Rationale: [why chosen]
        - Alternatives considered: [what else evaluated]

   d. **Phase 1: Data Model** - Generate and post as comment:

      Post comment with header `## Data Model`:
      - Extract entities from feature spec (Project content)
      - Entity name, fields, relationships
      - Validation rules from requirements
      - State transitions if applicable

   e. **Phase 1: API Contracts** - Generate and post as comment:

      Post comment with header `## API Contracts`:
      - For each user action → endpoint
      - Use standard REST/GraphQL patterns
      - Include request/response schemas
      - Document authentication requirements

   f. **Phase 1: Quickstart** - Generate and post as comment:

      Post comment with header `## Quickstart Guide`:
      - Test scenarios for validation
      - Integration patterns
      - Example usage

5. **Handle questions or blockers**:

   - **If needs human input**:
     - Post comment with specific questions
     - Add `ai:needs-input` label to Plan Issue:

       ```graphql
       mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
         issueUpdate(id: $id, input: $input) {
           issue { id labels { nodes { name } } }
           success
         }
       }
       ```

     - Update Plan Issue description to indicate waiting for input
     - Exit (in CI, job ends; human answers via comment, `ai:plan` label triggers retry)

   - **If planning successful**:
     - Update Plan Issue status to "Done"
     - Remove `ai:plan` label from Project (if in CI mode)

6. **Update Plan Issue description** with summary:

   ```graphql
   mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
     issueUpdate(id: $id, input: $input) {
       issue { id description }
       success
     }
   }
   ```

   Include:
   - Plan summary
   - Links to key comments (Research, Data Model, Contracts)
   - Tech stack decisions
   - Constitution compliance status
   - Next step: "Add `ai:tasks` label to Project when ready"

7. **Report completion**:
   - Plan Issue URL and identifier
   - Summary of artifacts generated
   - Any unresolved questions (if `ai:needs-input` was added)
   - Constitution check results
   - Suggested next step

## CI Mode Behavior

When triggered by `ai:plan` label on Project via webhook:

1. Parse webhook payload for Project ID
2. Load project and config
3. Create or resume Plan Issue
4. Generate all artifacts
5. If questions arise:
   - Add `ai:needs-input` label
   - Post questions as comment
   - Exit with status indicating waiting for input
6. If successful:
   - Mark Plan Issue as "Done"
   - Remove `ai:plan` label from Project
   - Exit with success

## Linear API Reference

### Get Project
```graphql
query GetProject($id: String!) {
  project(id: $id) {
    id
    name
    identifier
    content
    description
    url
    teams { nodes { id key } }
  }
}
```

### Create Issue
```graphql
mutation CreateIssue($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    issue { id identifier title url }
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

### Update Issue
```graphql
mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
  issueUpdate(id: $id, input: $input) {
    issue { id state { name } labels { nodes { name } } }
    success
  }
}
```

### Get Project Issues
```graphql
query GetProjectIssues($projectId: String!) {
  project(id: $projectId) {
    issues {
      nodes {
        id
        identifier
        title
        state { name }
      }
    }
  }
}
```

## Key Rules

- All artifacts are stored as comments on the Plan Issue
- The Project's `content` field contains the specification (source of truth)
- Use absolute identifiers for cross-referencing
- ERROR on gate failures or unresolved clarifications (in non-CI mode)
- In CI mode, post questions and add `ai:needs-input` label instead of erroring
