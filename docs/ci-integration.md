# CI Integration Guide

This guide explains how to set up Woodpecker CI to automate the Linear-native Spec-Driven Development workflow.

## Prerequisites

- Woodpecker CI instance (self-hosted or cloud)
- Linear workspace with API access
- GitHub repository with Woodpecker integration
- Claude API access (Anthropic)

## Step 1: Create API Tokens

### Linear API Token

1. Go to Linear Settings → API → Personal API keys
2. Click "Create key"
3. Name it "Spec Kit CI"
4. Copy the token (starts with `lin_api_`)

### Anthropic API Key

1. Go to console.anthropic.com
2. Navigate to API Keys
3. Create a new key for CI usage
4. Copy the key (starts with `sk-ant-`)

### GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic) with these scopes:
   - `repo` (full control of private repositories)
   - `workflow` (update GitHub Action workflows)
3. Copy the token

## Step 2: Configure Woodpecker Secrets

Add the following secrets to your Woodpecker repository:

```bash
# Via Woodpecker CLI
woodpecker secret add \
  --repository your-org/your-repo \
  --name linear_token \
  --value "lin_api_..."

woodpecker secret add \
  --repository your-org/your-repo \
  --name anthropic_api_key \
  --value "sk-ant-..."

woodpecker secret add \
  --repository your-org/your-repo \
  --name github_token \
  --value "ghp_..."
```

Or via Woodpecker UI:
1. Go to Repository Settings → Secrets
2. Add each secret with the names above

## Step 3: Configure Linear Labels

Create the required labels in your Linear team:

| Label | Color (suggested) | Description |
|-------|-------------------|-------------|
| `ai:plan` | Blue | Ready for planning phase |
| `ai:tasks` | Purple | Ready for task generation |
| `ai:ready` | Green | Ready for implementation |
| `ai:in-progress` | Yellow | Agent currently working |
| `ai:retry` | Orange | First failure, retrying |
| `ai:blocked` | Red | Needs human intervention |
| `ai:needs-input` | Pink | Agent has questions |
| `ai:review` | Cyan | PR awaiting review |

After creating labels, get their IDs:

```graphql
query {
  team(id: "your-team-id") {
    labels {
      nodes {
        id
        name
      }
    }
  }
}
```

## Step 4: Update linear-config.json

Update `linear-config.json` with your IDs:

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
    "done": "state-uuid-5"
  }
}
```

To get state IDs:

```graphql
query {
  team(id: "your-team-id") {
    states {
      nodes {
        id
        name
        type
      }
    }
  }
}
```

## Step 5: Configure Webhooks

See [webhook-setup.md](webhook-setup.md) for detailed webhook configuration.

## Step 6: Verify Setup

### Test Linear Connection

```bash
export LINEAR_TOKEN="lin_api_..."
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name } }"}'
```

### Test Webhook Delivery

1. Add `ai:plan` label to a test Project in Linear
2. Check Woodpecker for triggered job
3. Verify job starts and can authenticate

## CI Job Reference

### plan-project.yml

**Trigger:** `ai:plan` label added to Project

**Actions:**
1. Fetches Project content (specification)
2. Creates Plan Issue
3. Generates and posts artifact comments
4. Updates Plan Issue status

**Success:** Plan Issue marked "Done", `ai:plan` removed
**Needs Input:** `ai:needs-input` label added

### generate-tasks.yml

**Trigger:** `ai:tasks` label added to Project

**Actions:**
1. Reads Plan Issue and comments
2. Creates Milestones
3. Creates Issues with blocking relations
4. Posts summary on Plan Issue

**Success:** `ai:tasks` removed
**Needs Input:** `ai:needs-input` label added

### implement-issue.yml

**Trigger:** `ai:ready` label added to Issue

**Actions:**
1. Checks blocking relations
2. Creates feature branch
3. Implements task
4. Creates Pull Request
5. Updates Issue status

**Success:** Issue in "In Review"
**Retry:** `ai:retry` label added
**Blocked:** `ai:blocked` label added

### retry-issue.yml

**Trigger:** `ai:retry` label on Issue

**Actions:**
1. Loads previous error context
2. Attempts to fix issues
3. Re-runs validation

**Success:** PR created/updated
**Blocked:** `ai:blocked` label added

### address-feedback.yml

**Trigger:** PR review with changes requested

**Actions:**
1. Fetches review comments
2. Addresses feedback
3. Pushes new commits
4. Comments on Linear Issue

## Troubleshooting

### Job not triggering

1. Verify webhook is configured correctly
2. Check Woodpecker webhook logs
3. Ensure label IDs match configuration

### Authentication failures

1. Verify secrets are set correctly
2. Check token permissions
3. Test tokens with curl commands above

### Job fails immediately

1. Check job logs in Woodpecker
2. Verify Claude image is available
3. Check LINEAR_TOKEN is accessible

### Claude errors

1. Verify ANTHROPIC_API_KEY is set
2. Check API quota and limits
3. Review Claude output in job logs

## Security Considerations

- Store all tokens as secrets, never in code
- Use short-lived tokens where possible
- Limit GitHub token scope to necessary permissions
- Consider IP allowlisting for API tokens
- Audit webhook endpoints regularly
