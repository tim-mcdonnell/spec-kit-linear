# Spec Kit Linear

*Linear-native Spec-Driven Development*

**A Linear-integrated toolkit for structured software development. Specifications become Linear Projects, tasks become Issues, and CI automation handles planning and implementation.**

## What is Spec Kit Linear?

Spec Kit Linear transforms Spec-Driven Development into a **Linear-native workflow** where:

- **Specifications** are stored as Linear Project content
- **Planning artifacts** are posted as Issue comments
- **Tasks** become Linear Issues with Milestones
- **Blocking relations** enforce workflow dependencies
- **CI automation** handles planning, task generation, and implementation

Everything lives in Linear. No scattered markdown files. No manual syncing. Just structured development backed by your existing project management tool.

## Getting Started

- [Installation Guide](installation.md)
- [Quick Start Guide](quickstart.md)
- [CI Integration](ci-integration.md)
- [Webhook Setup](webhook-setup.md)

## The Workflow

### Phase 1: Interactive Specification

Use Claude Code to create and refine specifications that are stored directly in Linear:

```
/speckit.specify Build a task management app with Kanban boards
/speckit.clarify Focus on security requirements
```

### Phase 2: Planning (CI-Triggered)

Add the `ai:plan` label to your Linear Project. CI automation creates a Plan Issue with research, data models, and API contracts as comments.

### Phase 3: Task Generation (CI-Triggered)

Add the `ai:tasks` label. CI creates Milestones and Issues with blocking relations to enforce dependencies.

### Phase 4: Implementation (Per-Issue CI)

Add the `ai:ready` label to individual Issues. CI implements the code, runs tests, and creates Pull Requests.

### Phase 5: Review and Merge

Review PRs in GitHub. Merge to auto-close Linear Issues. Request changes to trigger CI feedback addressing.

## Core Philosophy

Spec-Driven Development is a structured process that emphasizes:

- **Intent-driven development** where specifications define the "what" before the "how"
- **Rich specification creation** using guardrails and organizational principles
- **Multi-step refinement** rather than one-shot code generation from prompts
- **Linear-native storage** so everything lives in your existing project management tool

## Label System

| Label | Applied By | Meaning |
|-------|------------|---------|
| `ai:plan` | Human | Ready for planning phase |
| `ai:tasks` | Human | Plan approved, generate tasks |
| `ai:ready` | Human | Issue ready to be worked |
| `ai:in-progress` | Agent | Currently working |
| `ai:blocked` | Agent | Needs human intervention |
| `ai:review` | Agent | PR created, awaiting review |

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

## Learn More

- [AGENTS.md](../AGENTS.md) - Detailed workflow documentation
- [CI Integration](ci-integration.md) - CI setup guide
- [Webhook Setup](webhook-setup.md) - Webhook configuration

## Contributing

Please see our [Contributing Guide](../CONTRIBUTING.md) for information on how to contribute to this project.

## Support

For support, please check our [Support Guide](../SUPPORT.md) or open an issue on GitHub.
