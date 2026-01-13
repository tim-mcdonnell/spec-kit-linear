# AGENTS.md

## About Spec Kit Linear

**Spec Kit Linear** is a Linear-native implementation of Spec-Driven Development (SDD) - a methodology that emphasizes creating clear specifications before implementation. Everything is stored in Linear: specifications as Projects, planning artifacts as Issue comments, tasks as Issues with Milestones, and blocking relations to enforce workflow dependencies.

The toolkit provides:
- **Interactive Commands**: Terminal-based commands for creating and clarifying specifications
- **CI/CD Automation**: Woodpecker CI jobs triggered by Linear labels for planning, task generation, and implementation
- **Linear GraphQL Integration**: Python client library for all Linear API operations

---

## Workflow Overview

### Phase 1: Interactive (Terminal with Claude Code)

```
You + Claude → /speckit.specify → Creates Linear Project with spec in content field
You + Claude → /speckit.clarify → Updates Project content with clarifications
You → Review Project in Linear UI
You → Add "ai:plan" label when ready
```

### Phase 2: Planning (CI-Triggered)

```
"ai:plan" label added → Webhook → Woodpecker CI
Claude agent:
  1. Creates "Plan: [Project Name]" Issue
  2. Posts research findings as comment
  3. Posts data model as comment
  4. Posts API contracts as comment
  5. Updates Plan Issue description with summary
  6. If blocked: adds "ai:needs-input" label, exits
  7. If successful: marks Plan Issue "Done"
You → Add "ai:tasks" label when ready
```

### Phase 3: Task Generation (CI-Triggered)

```
"ai:tasks" label added → Webhook → Woodpecker CI
Claude agent:
  1. Reads Plan Issue and artifact comments
  2. Creates Milestones for phases
  3. Creates Issues for tasks with blocking relations
  4. Posts summary on Plan Issue
You → Add "ai:ready" to issues you want worked
```

### Phase 4: Implementation (Per-Issue CI)

```
"ai:ready" label on Issue → Webhook → Woodpecker CI
Claude agent:
  1. Checks blocking relations
  2. Creates feature branch
  3. Implements task (code + tests)
  4. Creates PR with "Fixes TIM-XXX" reference
  5. Updates Issue status to "In Review"
```

### Phase 5: PR Review

```
You → Review PR in GitHub
  - Approve → Merge → Linear auto-closes Issue
  - Request changes → CI triggers retry → Agent addresses feedback
```

---

## Label System

| Label | Applied By | Meaning |
|-------|------------|---------|
| `ai:plan` | Human | Project ready for planning phase |
| `ai:tasks` | Human | Plan approved, generate tasks |
| `ai:ready` | Human | Issue ready to be worked |
| `ai:in-progress` | Agent | Currently working on issue |
| `ai:retry` | Agent | First failure, will retry once |
| `ai:blocked` | Agent | Needs human intervention |
| `ai:needs-input` | Agent | Has specific questions |
| `ai:review` | Agent | PR created, awaiting review |

---

## Project Structure

```
spec-kit-linear/
├── src/
│   ├── specify_cli/          # CLI for interactive commands
│   │   └── __init__.py       # Main CLI implementation
│   └── linear/               # Linear GraphQL client library
│       ├── __init__.py       # Package exports
│       ├── client.py         # HTTP client with auth
│       ├── queries.py        # Read operations
│       ├── mutations.py      # Write operations
│       └── types.py          # Type definitions
├── templates/
│   └── commands/             # Command templates
│       ├── specify.md        # Create Linear Project
│       ├── clarify.md        # Clarify specification
│       ├── plan.md           # Generate planning artifacts
│       ├── tasks.md          # Generate milestones/issues
│       └── implement.md      # Implement single issue
├── .woodpecker/              # CI job definitions
│   ├── plan-project.yml      # Triggered by ai:plan
│   ├── generate-tasks.yml    # Triggered by ai:tasks
│   ├── implement-issue.yml   # Triggered by ai:ready
│   ├── retry-issue.yml       # Triggered by ai:retry
│   └── address-feedback.yml  # Triggered by PR review
├── linear-config.json        # Team/label/state IDs
└── docs/
    ├── ci-integration.md     # CI setup guide
    └── webhook-setup.md      # Webhook configuration
```

---

## Linear GraphQL Client

The `src/linear/` package provides a typed Python client for Linear's GraphQL API.

### Quick Start

```python
from linear import LinearClient, LinearQueries, LinearMutations

# Initialize client (uses LINEAR_TOKEN env var)
client = LinearClient()
queries = LinearQueries(client)
mutations = LinearMutations(client)

# Get an issue
issue = queries.get_issue("TIM-123")
print(f"{issue.identifier}: {issue.title}")

# Create a comment
comment = mutations.create_comment(issue.id, "## Update\nWork completed.")

# Update issue state
mutations.update_issue(issue.id, state_id="done-state-uuid")
```

### Key Operations

**Queries:**
- `get_issue(id)` - Get issue by ID or identifier
- `get_project(id)` - Get project with content
- `get_issue_comments(id)` - Get all comments on issue
- `get_team(id)` - Get team with states and labels
- `find_plan_issue(project_id)` - Find Plan Issue for project

**Mutations:**
- `create_project(name, team_ids, content)` - Create new project
- `update_project(id, content)` - Update project content
- `create_issue(title, team_id, project_id)` - Create issue
- `update_issue(id, state_id, label_ids)` - Update issue
- `create_comment(issue_id, body)` - Add comment
- `create_milestone(project_id, name)` - Create milestone
- `create_blocking_relation(blocker_id, blocked_id)` - Create block relation

---

## Configuration

### linear-config.json

```json
{
  "teamId": "your-team-uuid",
  "labels": {
    "ai:plan": "label-uuid",
    "ai:tasks": "label-uuid",
    "ai:ready": "label-uuid",
    "ai:in-progress": "label-uuid",
    "ai:retry": "label-uuid",
    "ai:blocked": "label-uuid",
    "ai:needs-input": "label-uuid",
    "ai:review": "label-uuid"
  },
  "states": {
    "backlog": "state-uuid",
    "todo": "state-uuid",
    "inProgress": "state-uuid",
    "inReview": "state-uuid",
    "done": "state-uuid"
  }
}
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LINEAR_TOKEN` | Yes | Linear API token |
| `ANTHROPIC_API_KEY` | Yes (CI) | Claude API key for CI jobs |
| `GITHUB_TOKEN` | Yes (CI) | GitHub token for PR creation |

---

## CI/CD Integration

### Woodpecker CI Setup

1. Add secrets to Woodpecker:
   - `linear_token` - Linear API token
   - `anthropic_api_key` - Claude API key
   - `github_token` - GitHub PAT

2. Configure Linear webhooks to trigger Woodpecker jobs

3. Configure GitHub webhooks for PR review events

See `docs/ci-integration.md` for detailed setup instructions.

### Webhook Events

**Linear → Woodpecker:**
- `ai:plan` label on Project → `plan-project.yml`
- `ai:tasks` label on Project → `generate-tasks.yml`
- `ai:ready` label on Issue → `implement-issue.yml`
- `ai:retry` label on Issue → `retry-issue.yml`

**GitHub → Woodpecker:**
- PR review with changes requested → `address-feedback.yml`

---

## Commands Reference

### /speckit.specify

Creates a Linear Project with the specification in the `content` field.

**Usage:**
```
/speckit.specify Add user authentication with OAuth2 support
```

**Creates:**
- Linear Project with generated name
- Specification stored in `content` field
- Validation against quality criteria

### /speckit.clarify

Identifies underspecified areas and updates the Project content.

**Usage:**
```
/speckit.clarify [project-identifier]
```

**Process:**
- Asks up to 5 targeted questions
- Updates Project content with clarifications
- Reports coverage status

### /speckit.plan (CI-Triggered)

Creates Plan Issue and generates planning artifacts.

**Triggered by:** `ai:plan` label on Project

**Creates:**
- Plan Issue with title "Plan: [Project Name]"
- Research findings comment
- Data model comment
- API contracts comment

### /speckit.tasks (CI-Triggered)

Generates Milestones and Issues from Plan Issue.

**Triggered by:** `ai:tasks` label on Project

**Creates:**
- Milestones for each phase
- Issues for each task
- Blocking relations between issues

### /speckit.implement (CI-Triggered)

Implements a single Issue by creating a branch and PR.

**Triggered by:** `ai:ready` label on Issue

**Process:**
1. Checks blocking relations
2. Creates feature branch
3. Writes code and tests
4. Creates Pull Request
5. Updates Issue status

---

## General Practices

- Changes to `src/specify_cli/__init__.py` require a version bump in `pyproject.toml` and `CHANGELOG.md` entry
- All specifications are stored in Linear - no local files
- Blocking relations enforce workflow order
- CI jobs are idempotent - safe to retry

---

*This documentation reflects the Linear-native workflow. For the original file-based workflow, see the spec-kit repository.*
