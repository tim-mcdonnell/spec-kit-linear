<div align="center">
    <img src="./media/logo_large.webp" alt="Spec Kit Logo" width="200" height="200"/>
    <h1>Spec Kit Linear</h1>
    <h3><em>Linear-native Spec-Driven Development</em></h3>
</div>

<p align="center">
    <strong>A Linear-integrated toolkit for structured software development. Specifications become Linear Projects, tasks become Issues, and CI automation handles planning and implementation.</strong>
</p>

---

## Table of Contents

- [What is Spec Kit Linear?](#what-is-spec-kit-linear)
- [Quick Start](#quick-start)
- [The Workflow](#the-workflow)
- [Configuration](#configuration)
- [Commands Reference](#commands-reference)
- [CI/CD Integration](#cicd-integration)
- [Label System](#label-system)
- [Prerequisites](#prerequisites)
- [Learn More](#learn-more)

## What is Spec Kit Linear?

Spec Kit Linear transforms Spec-Driven Development into a Linear-native workflow where:

- **Specifications** are stored as Linear Project content
- **Planning artifacts** are posted as Issue comments
- **Tasks** become Linear Issues with Milestones
- **Blocking relations** enforce workflow dependencies
- **CI automation** handles planning, task generation, and implementation

Everything lives in Linear. No scattered markdown files. No manual syncing. Just structured development backed by your existing project management tool.

## Quick Start

### 1. Install Dependencies

```bash
# Install the Python package
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Set up Linear API token
export LINEAR_TOKEN="lin_api_..."
```

### 2. Configure Linear

Create `linear-config.json` with your team and label IDs:

```json
{
  "teamId": "your-team-uuid",
  "labels": {
    "ai:plan": "label-uuid",
    "ai:tasks": "label-uuid",
    "ai:ready": "label-uuid"
  },
  "states": {
    "todo": "state-uuid",
    "inProgress": "state-uuid",
    "done": "state-uuid"
  }
}
```

### 3. Create Your First Spec

With Claude Code:

```
/speckit.specify Build a task management app with Kanban boards, user assignments, and real-time updates
```

This creates a Linear Project with your specification in the `content` field.

### 4. Trigger Automation

1. Review the Project in Linear
2. Add `ai:plan` label when ready → CI generates planning artifacts
3. Add `ai:tasks` label → CI creates Milestones and Issues
4. Add `ai:ready` to issues → CI implements and creates PRs

## The Workflow

### Phase 1: Interactive Specification (Terminal)

```
You + Claude → /speckit.specify → Linear Project created
You + Claude → /speckit.clarify → Project content updated
You → Review in Linear UI → Add ai:plan label
```

### Phase 2: Planning (CI-Triggered)

```
ai:plan label → Woodpecker CI → Claude agent:
  ├── Creates "Plan: [Project Name]" Issue
  ├── Posts Research comment
  ├── Posts Data Model comment
  ├── Posts API Contracts comment
  └── Marks Plan Issue "Done"
```

### Phase 3: Task Generation (CI-Triggered)

```
ai:tasks label → Woodpecker CI → Claude agent:
  ├── Creates Milestones (Setup, Foundational, User Stories...)
  ├── Creates Issues for each task
  ├── Creates blocking relations
  └── Posts summary on Plan Issue
```

### Phase 4: Implementation (Per-Issue CI)

```
ai:ready label on Issue → Woodpecker CI → Claude agent:
  ├── Checks blocking relations
  ├── Creates feature branch
  ├── Implements code + tests
  ├── Creates Pull Request
  └── Updates Issue → "In Review"
```

### Phase 5: Review & Merge

```
You → Review PR in GitHub
  ├── Approve → Merge → Linear auto-closes Issue
  └── Request changes → CI addresses feedback
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LINEAR_TOKEN` | Yes | Linear API token |
| `ANTHROPIC_API_KEY` | CI only | Claude API key |
| `GITHUB_TOKEN` | CI only | GitHub PAT for PRs |

### linear-config.json

```json
{
  "teamId": "your-team-uuid",
  "labels": {
    "ai:plan": "uuid",
    "ai:tasks": "uuid",
    "ai:ready": "uuid",
    "ai:in-progress": "uuid",
    "ai:retry": "uuid",
    "ai:blocked": "uuid",
    "ai:needs-input": "uuid",
    "ai:review": "uuid"
  },
  "states": {
    "backlog": "uuid",
    "todo": "uuid",
    "inProgress": "uuid",
    "inReview": "uuid",
    "done": "uuid"
  }
}
```

## Commands Reference

### Interactive Commands (Terminal)

| Command | Description |
|---------|-------------|
| `/speckit.constitution` | Create project governance principles |
| `/speckit.specify [description]` | Create Linear Project with specification |
| `/speckit.clarify [project-id]` | Clarify underspecified areas |

### CI-Triggered Commands

| Trigger | Command | Description |
|---------|---------|-------------|
| `ai:plan` label | `/speckit.plan` | Create Plan Issue with artifacts |
| `ai:tasks` label | `/speckit.tasks` | Generate Milestones and Issues |
| `ai:ready` label | `/speckit.implement` | Implement Issue, create PR |

## CI/CD Integration

### Woodpecker CI Jobs

| Job | Trigger | Description |
|-----|---------|-------------|
| `plan-project.yml` | `ai:plan` on Project | Generate planning artifacts |
| `generate-tasks.yml` | `ai:tasks` on Project | Create milestones/issues |
| `implement-issue.yml` | `ai:ready` on Issue | Implement and create PR |
| `retry-issue.yml` | `ai:retry` on Issue | Retry failed implementation |
| `address-feedback.yml` | PR changes requested | Address review feedback |

### Setup

1. Add secrets to Woodpecker:
   - `linear_token`
   - `anthropic_api_key`
   - `github_token`

2. Configure Linear webhooks → See [docs/webhook-setup.md](docs/webhook-setup.md)

3. Configure GitHub webhooks for PR reviews

Full setup guide: [docs/ci-integration.md](docs/ci-integration.md)

## Label System

| Label | Applied By | Meaning |
|-------|------------|---------|
| `ai:plan` | Human | Ready for planning phase |
| `ai:tasks` | Human | Plan approved, generate tasks |
| `ai:ready` | Human | Issue ready to be worked |
| `ai:in-progress` | Agent | Currently working |
| `ai:retry` | Agent | First failure, will retry |
| `ai:blocked` | Agent | Needs human intervention |
| `ai:needs-input` | Agent | Has specific questions |
| `ai:review` | Agent | PR created, awaiting review |

## Project Structure

```
spec-kit-linear/
├── src/
│   ├── specify_cli/          # CLI for interactive commands
│   └── linear/               # Linear GraphQL client
│       ├── client.py         # HTTP client
│       ├── queries.py        # Read operations
│       ├── mutations.py      # Write operations
│       └── types.py          # Type definitions
├── templates/
│   └── commands/             # Command templates
├── .woodpecker/              # CI job definitions
├── linear-config.json        # Configuration
└── docs/
    ├── ci-integration.md     # CI setup guide
    └── webhook-setup.md      # Webhook configuration
```

## Prerequisites

- **Python 3.11+**
- **uv** for package management
- **Linear** workspace with API access
- **Claude Code** (or compatible AI assistant)
- **Woodpecker CI** for automation (optional but recommended)
- **GitHub** for PR integration

## Learn More

- [AGENTS.md](AGENTS.md) - Detailed workflow documentation
- [docs/ci-integration.md](docs/ci-integration.md) - CI setup guide
- [docs/webhook-setup.md](docs/webhook-setup.md) - Webhook configuration

## Core Philosophy

Spec-Driven Development emphasizes:

- **Intent-driven development**: Specifications define the "what" before the "how"
- **Rich specification creation**: Using guardrails and organizational principles
- **Multi-step refinement**: Rather than one-shot code generation
- **Linear-native storage**: Everything in your existing project management tool

## Differences from Spec Kit

| Feature | Spec Kit | Spec Kit Linear |
|---------|----------|-----------------|
| Spec storage | Local files | Linear Projects |
| Task tracking | Markdown files | Linear Issues |
| Dependencies | Manual | Blocking relations |
| Automation | Manual workflow | CI-triggered |
| Review | Git diffs | Linear + GitHub |

---

## License

MIT License - See [LICENSE](LICENSE) for details.

## Acknowledgements

Built on the foundations of [Spec Kit](https://github.com/github/spec-kit) with Linear integration.
