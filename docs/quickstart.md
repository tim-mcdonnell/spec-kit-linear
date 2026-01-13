# Quick Start Guide

This guide will help you get started with Spec-Driven Development using Spec Kit Linear, a Linear-native workflow for building software through specifications.

## Overview

Spec Kit Linear integrates directly with Linear to manage your entire development workflow:

- **Specifications** are stored as Linear Projects (in the `content` field)
- **Planning artifacts** are posted as Issue comments
- **Tasks** are Linear Issues organized into Milestones
- **Workflow dependencies** are enforced through blocking relations
- **CI automation** is triggered by Linear labels via Woodpecker CI

## Prerequisites

- [Linear](https://linear.app) workspace with API access
- AI coding agent: [Claude Code](https://www.anthropic.com/claude-code) or similar
- Woodpecker CI (for automated planning and implementation)
- GitHub repository for code and Pull Requests

## The Workflow

### Phase 1: Create the Specification (Interactive)

**In your AI agent's terminal**, use the `/speckit.specify` command to describe what you want to build. Focus on the **what** and **why**, not the tech stack.

```markdown
/speckit.specify Build an application that helps me organize my photos in separate albums. Albums are grouped by date and can be reorganized by dragging and dropping. Within each album, photos are previewed in a tile-like interface.
```

This creates a **Linear Project** with:

- A generated project name (e.g., "Photo Album Organizer")
- The full specification stored in the Project's `content` field
- Quality validation against Spec-Driven Development criteria

### Phase 2: Clarify Requirements (Interactive)

**In the terminal**, use the `/speckit.clarify` command to identify and resolve ambiguities. Provide the Project identifier.

```markdown
/speckit.clarify TIM-P-001
```

The agent will:

- Analyze the specification for gaps
- Ask up to 5 targeted clarification questions
- Update the Project content with your answers

### Phase 3: Review in Linear

Open your Linear Project and review the specification. When you are satisfied:

**Add the `ai:plan` label to the Project.**

This triggers the CI-automated planning phase.

### Phase 4: Planning (CI-Triggered)

When the `ai:plan` label is added, Woodpecker CI automatically:

1. Creates a "Plan: [Project Name]" Issue
2. Posts research findings as a comment
3. Posts data model as a comment
4. Posts API contracts as a comment
5. Updates the Plan Issue with a summary

Review the planning artifacts in Linear. When ready:

**Add the `ai:tasks` label to the Project.**

### Phase 5: Task Generation (CI-Triggered)

When the `ai:tasks` label is added, CI automatically:

1. Creates Milestones for each phase
2. Creates Issues for each task
3. Sets up blocking relations between Issues
4. Posts a summary on the Plan Issue

Review the generated tasks in Linear. For each Issue you want implemented:

**Add the `ai:ready` label to the Issue.**

### Phase 6: Implementation (CI-Triggered)

For each Issue with the `ai:ready` label, CI automatically:

1. Checks that blocking Issues are complete
2. Creates a feature branch
3. Implements the task (code and tests)
4. Creates a Pull Request with "Fixes TIM-XXX" reference
5. Updates the Issue status to "In Review"

### Phase 7: Review and Merge

Review Pull Requests in GitHub:

- **Approve and Merge**: Linear auto-closes the Issue
- **Request Changes**: CI triggers a retry, agent addresses feedback

## Detailed Example: Building Taskify

Here is a complete example of building a team productivity platform.

### Step 1: Create the Specification

```markdown
/speckit.specify Develop Taskify, a team productivity platform. Users can create projects, add team members, assign tasks, comment, and move tasks between boards in Kanban style. For this initial phase, we have five predefined users (one product manager and four engineers) across three sample projects. Standard Kanban columns: To Do, In Progress, In Review, and Done. No login required for this MVP.
```

The agent creates a Linear Project with the full specification.

### Step 2: Clarify Requirements

```markdown
/speckit.clarify TIM-P-001
```

Example clarification session:

```
Q: How should task cards display assignee information?
Recommended: Option B - Show avatar and name
Reply with the option letter, "yes" to accept, or provide your own answer.

> yes

Q: Can users edit or delete comments made by others?
Suggested: Users can only edit/delete their own comments
Reply "yes" to accept, or provide your own answer.

> yes
```

### Step 3: Add Labels to Trigger CI

In Linear:

1. Add `ai:plan` label to the Project
2. Wait for Plan Issue to be created and populated
3. Review the planning artifacts
4. Add `ai:tasks` label to the Project
5. Review the generated Milestones and Issues
6. Add `ai:ready` label to Issues you want implemented

### Step 4: Review Pull Requests

As the agent implements each Issue, Pull Requests appear in GitHub. Review, request changes if needed, and merge when satisfied.

## Label Reference

| Label | Applied By | Meaning |
|-------|------------|---------|
| `ai:plan` | Human | Project ready for planning phase |
| `ai:tasks` | Human | Plan approved, generate tasks |
| `ai:ready` | Human | Issue ready to be implemented |
| `ai:in-progress` | Agent | Currently working on issue |
| `ai:retry` | Agent | First failure, will retry once |
| `ai:blocked` | Agent | Needs human intervention |
| `ai:needs-input` | Agent | Agent has specific questions |
| `ai:review` | Agent | PR created, awaiting review |

## Command Reference

### Interactive Commands (Terminal)

| Command | Description |
|---------|-------------|
| `/speckit.specify` | Create a Linear Project with the specification |
| `/speckit.clarify` | Clarify requirements and update Project content |

### CI-Triggered Commands

| Trigger | Action |
|---------|--------|
| `ai:plan` label on Project | Creates Plan Issue with artifacts |
| `ai:tasks` label on Project | Generates Milestones and Issues |
| `ai:ready` label on Issue | Implements task and creates PR |

## Key Principles

- **Be explicit** about what you are building and why
- **Avoid tech stack details** during specification phase
- **Iterate and refine** specifications before triggering planning
- **Review artifacts** in Linear before advancing to the next phase
- **Let the CI automation** handle implementation details

## Next Steps

- [CI Integration Guide](ci-integration.md) - Set up Woodpecker CI automation
- [Webhook Setup](webhook-setup.md) - Configure Linear webhooks
- [Spec-Driven Development Methodology](../spec-driven.md) - In-depth guidance
