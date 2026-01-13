# Installation Guide

## Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **uv** - Package management - [Install](https://docs.astral.sh/uv/)
- **Git** - [Download](https://git-scm.com/downloads)
- **Linear** - Workspace with API access
- **Claude Code** - [Install](https://www.anthropic.com/claude-code) (or compatible AI assistant)

For CI automation (optional but recommended):
- **Woodpecker CI** - Self-hosted or cloud instance
- **GitHub** - For PR integration

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/spec-kit-linear.git
cd spec-kit-linear
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Set Up Linear API Token

Create a Linear API token:

1. Go to Linear Settings > API > Personal API keys
2. Click "Create key"
3. Name it (e.g., "Spec Kit")
4. Copy the token (starts with `lin_api_`)

Set the environment variable:

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export LINEAR_TOKEN="lin_api_..."
```

### 4. Configure linear-config.json

The `linear-config.json` file maps your Linear team, labels, and workflow states to UUIDs. You can either:

**Option A: Use the setup command (recommended)**

```bash
uv run specify linear-setup
```

This interactively configures your Linear workspace.

**Option B: Manual configuration**

1. Get your team ID from Linear's GraphQL explorer:

```graphql
query {
  teams {
    nodes {
      id
      name
    }
  }
}
```

2. Create the required labels in Linear:

| Label | Description |
|-------|-------------|
| `ai:plan` | Ready for planning phase |
| `ai:tasks` | Ready for task generation |
| `ai:ready` | Issue ready for implementation |
| `ai:in-progress` | Agent currently working |
| `ai:retry` | First failure, retrying |
| `ai:blocked` | Needs human intervention |
| `ai:needs-input` | Agent has questions |
| `ai:review` | PR awaiting review |

3. Get label and state IDs:

```graphql
query {
  team(id: "your-team-id") {
    labels {
      nodes { id name }
    }
    states {
      nodes { id name type }
    }
  }
}
```

4. Update `linear-config.json`:

```json
{
  "teamId": "your-team-uuid",
  "labels": {
    "ai:plan": "label-uuid-1",
    "ai:tasks": "label-uuid-2",
    "ai:ready": "label-uuid-3",
    "ai:in-progress": "label-uuid-4",
    "ai:retry": "label-uuid-5",
    "ai:blocked": "label-uuid-6",
    "ai:needs-input": "label-uuid-7",
    "ai:review": "label-uuid-8"
  },
  "states": {
    "backlog": "state-uuid-1",
    "todo": "state-uuid-2",
    "inProgress": "state-uuid-3",
    "inReview": "state-uuid-4",
    "done": "state-uuid-5",
    "canceled": "state-uuid-6"
  }
}
```

## Verification

### Test Linear Connection

```bash
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name } }"}'
```

You should see your Linear user information in the response.

### Verify Commands

With Claude Code, you should have access to:

- `/speckit.constitution` - Create project governance principles
- `/speckit.specify` - Create Linear Project with specification
- `/speckit.clarify` - Clarify underspecified areas

## CI Setup (Optional)

For automated planning, task generation, and implementation, you need:

### Environment Variables for CI

| Variable | Required | Description |
|----------|----------|-------------|
| `LINEAR_TOKEN` | Yes | Linear API token |
| `ANTHROPIC_API_KEY` | Yes | Claude API key for AI operations |
| `GITHUB_TOKEN` | Yes | GitHub PAT for PR creation |

### Woodpecker CI Secrets

```bash
woodpecker secret add --repository your-org/your-repo --name linear_token --value "lin_api_..."
woodpecker secret add --repository your-org/your-repo --name anthropic_api_key --value "sk-ant-..."
woodpecker secret add --repository your-org/your-repo --name github_token --value "ghp_..."
```

See [ci-integration.md](ci-integration.md) for complete CI setup instructions.

## Troubleshooting

### LINEAR_TOKEN not found

Ensure the environment variable is set and exported:

```bash
echo $LINEAR_TOKEN
# Should print your token
```

If empty, add to your shell profile and reload:

```bash
source ~/.zshrc  # or ~/.bashrc
```

### API authentication failed

1. Verify your token is valid and not expired
2. Check the token has correct permissions
3. Test with curl command above

### linear-config.json validation errors

1. Verify all UUIDs are valid (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
2. Ensure all required fields are populated
3. Check that label and state names match your Linear workspace

### Git Credential Manager on Linux

If you're having issues with Git authentication on Linux:

```bash
wget https://github.com/git-ecosystem/git-credential-manager/releases/download/v2.6.1/gcm-linux_amd64.2.6.1.deb
sudo dpkg -i gcm-linux_amd64.2.6.1.deb
git config --global credential.helper manager
rm gcm-linux_amd64.2.6.1.deb
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Complete walkthrough
- [CI Integration](ci-integration.md) - Set up automated workflows
- [Webhook Setup](webhook-setup.md) - Configure Linear webhooks
