---
description: Implement a Linear Issue by creating a branch, writing code, and creating a PR. Triggered by `ai:ready` label in CI or manually.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The input should include the Issue identifier (e.g., "TIM-123").

## Outline

This command implements a single Linear Issue by:
1. Checking blockers
2. Creating a feature branch
3. Writing code and tests
4. Creating a Pull Request
5. Updating the Issue status

In CI mode, this is triggered when the `ai:ready` label is added to an Issue.

### Execution Steps

1. **Load the Issue and context**:

   ```graphql
   query GetIssue($id: String!) {
     issue(id: $id) {
       id
       identifier
       title
       description
       priority
       url
       branchName
       team { id key }
       state { id name type }
       project {
         id
         name
         content
       }
       milestone { id name }
       labels { nodes { id name } }
       relations {
         nodes {
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
   ```

   - Parse Issue ID from input or CI webhook payload
   - Load `linear-config.json` for state IDs
   - Verify `LINEAR_TOKEN` and `GITHUB_TOKEN` are set
   - Load Project content (spec) for context
   - Find Plan Issue for additional context (artifact comments)

2. **Check blocking relations**:

   From the Issue's relations, check all "blocked by" relations:

   ```python
   incomplete_blockers = []
   for relation in issue.relations:
       if relation.type == "blocked_by":
           if relation.related_issue.state.name not in ["Done", "Completed", "Canceled"]:
               incomplete_blockers.append(relation.related_issue.identifier)
   ```

   - If blockers are incomplete:
     - Post comment: "Blocked by: TIM-001, TIM-002 (not yet complete)"
     - Add `ai:blocked` label
     - Exit

3. **Update Issue status to "In Progress"**:

   ```graphql
   mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
     issueUpdate(id: $id, input: $input) {
       issue { id state { name } }
       success
     }
   }
   ```

   - Update state to "In Progress" (using state ID from config)
   - Add `ai:in-progress` label
   - Remove `ai:ready` label

4. **Create feature branch**:

   Branch naming convention:
   ```
   issue-{identifier}-{short-title}
   ```

   Example: `issue-TIM-123-user-authentication`

   ```bash
   git checkout main
   git pull origin main
   git checkout -b issue-TIM-123-user-authentication
   ```

5. **Parse task requirements** from Issue description:

   Extract from the Issue description:
   - **Objective**: What to accomplish
   - **Files**: What to create/modify
   - **Requirements**: Specific implementation details
   - **Acceptance Criteria**: What must be true when done

   Also load context from:
   - Project content (spec)
   - Plan Issue comments (data model, API contracts)
   - Related issues (for patterns/consistency)

6. **Execute implementation**:

   For each file in the task:
   - Follow TDD if tests are required:
     1. Write failing test
     2. Run test to confirm failure
     3. Write minimal code to pass
     4. Run test to confirm pass
   - Otherwise:
     1. Write implementation
     2. Run linting/type checks
     3. Run existing tests

   **Commit incrementally** with meaningful messages:
   ```bash
   git add <specific-files>
   git commit -m "Fixes TIM-123: <description of change>"
   ```

7. **Run validation**:

   - Run project's test suite
   - Run linting
   - Run type checking (if applicable)

   **If validation fails**:
   - First failure: Add `ai:retry` label, post error as comment, exit
   - On retry (if `ai:retry` label was present):
     - Attempt to fix the issue
     - If still failing: Add `ai:blocked` label, post full error context, exit

8. **Push branch and create PR**:

   ```bash
   git push -u origin issue-TIM-123-user-authentication
   ```

   Create PR using GitHub CLI or API:
   ```bash
   gh pr create --title "TIM-123: [Task Title]" --body "$(cat <<'EOF'
   ## Summary
   [Brief description of changes]

   ## Changes
   - [List of changes]

   ## Testing
   - [How this was tested]

   ## Linear Issue
   Fixes TIM-123

   ## Checklist
   - [ ] Tests pass
   - [ ] Code follows project conventions
   - [ ] Documentation updated (if needed)
   EOF
   )"
   ```

9. **Update Issue in Linear**:

   ```graphql
   mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
     issueUpdate(id: $id, input: $input) {
       issue { id state { name } }
       success
     }
   }
   ```

   - Update state to "In Review"
   - Add `ai:review` label
   - Remove `ai:in-progress` label

   Post comment with PR link:
   ```graphql
   mutation AddComment($input: CommentCreateInput!) {
     commentCreate(input: $input) {
       comment { id }
       success
     }
   }
   ```

10. **Report completion**:
    - PR URL
    - Branch name
    - Summary of changes
    - Files modified
    - Tests added/modified
    - Issue updated status

## Error Handling

### First Failure (ai:retry)

When tests/linting fails on first attempt:

1. Add `ai:retry` label to Issue
2. Post comment with error details:
   ```markdown
   ## Implementation Failed - Retry Scheduled

   **Error Type**: [Test failure / Lint error / Type error]

   **Details**:
   ```
   [Error output]
   ```

   **Next Steps**: CI will retry this issue automatically.
   ```
3. Exit with retry status

### Retry Also Fails (ai:blocked)

When retry attempt also fails:

1. Remove `ai:retry` label
2. Add `ai:blocked` label
3. Post detailed comment:
   ```markdown
   ## Implementation Blocked - Human Review Needed

   **Attempts**: 2

   **Error Summary**:
   [Concise error description]

   **Full Error Output**:
   ```
   [Complete error logs]
   ```

   **Suggested Fixes**:
   - [Possible solution 1]
   - [Possible solution 2]

   **Files Changed**:
   - [List of files with partial changes]

   Please review and either:
   1. Manually fix the issue and remove `ai:blocked` label
   2. Update the task description with more context
   3. Split this task into smaller pieces
   ```
4. Exit with blocked status

## CI Mode Behavior

When triggered by `ai:ready` label on Issue via webhook:

1. Parse webhook payload for Issue ID
2. Load issue and check blockers
3. If blocked → add `ai:blocked` label, exit
4. Update status to "In Progress"
5. Create branch and implement
6. If tests fail:
   - First try → add `ai:retry`, exit (CI will retry)
   - Retry → add `ai:blocked`, exit
7. Push branch, create PR
8. Update status to "In Review"
9. Exit with success

### Retry Behavior

When triggered by `ai:retry` label:

1. Load previous state from Issue comments
2. Attempt to fix the identified issues
3. Re-run validation
4. If still failing → `ai:blocked`
5. If passing → create/update PR, update status

## Linear API Reference

### Get Issue with Full Context
```graphql
query GetIssue($id: String!) {
  issue(id: $id) {
    id
    identifier
    title
    description
    priority
    url
    branchName
    team { id key }
    state { id name type }
    project {
      id
      name
      content
    }
    milestone { id name }
    labels { nodes { id name } }
    relations {
      nodes {
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

### Add Comment
```graphql
mutation AddComment($input: CommentCreateInput!) {
  commentCreate(input: $input) {
    comment { id body }
    success
  }
}
```

### Get Issue Comments (for retry context)
```graphql
query GetIssueComments($id: String!) {
  issue(id: $id) {
    comments {
      nodes {
        id
        body
        createdAt
      }
    }
  }
}
```

## Key Rules

- Check blockers before starting work
- Use Linear's branch name suggestion when available
- Commit with "Fixes TIM-XXX" to enable auto-linking
- Update Issue status at each phase transition
- First failure triggers retry, second failure requires human intervention
- All errors are logged as Issue comments for traceability
