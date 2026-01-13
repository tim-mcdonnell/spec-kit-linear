# Webhook Setup Guide

This guide explains how to configure webhooks to connect Linear and GitHub to your Woodpecker CI for automated workflow execution.

## Overview

The Linear-native workflow uses webhooks to trigger CI jobs:

```
Linear                          Woodpecker CI
┌─────────────────┐            ┌──────────────────┐
│ Label added to  │───────────▶│ plan-project.yml │
│ Project: ai:plan│            │ generate-tasks   │
│ Project: ai:tasks            │ implement-issue  │
│ Issue: ai:ready │            │ retry-issue      │
└─────────────────┘            └──────────────────┘

GitHub                          Woodpecker CI
┌─────────────────┐            ┌──────────────────┐
│ PR Review:      │───────────▶│ address-feedback │
│ changes_requested            │                  │
└─────────────────┘            └──────────────────┘
```

## Linear Webhook Configuration

### Step 1: Create Webhook Endpoint

Your Woodpecker CI needs a webhook endpoint. The format is typically:

```
https://your-woodpecker.example.com/hook?access_token=YOUR_HOOK_TOKEN
```

Or if using a webhook relay:

```
https://webhook-relay.example.com/linear-to-woodpecker
```

### Step 2: Configure Linear Webhook

1. Go to Linear Settings → API → Webhooks
2. Click "New webhook"
3. Configure:
   - **Label**: "Spec Kit CI Trigger"
   - **URL**: Your Woodpecker webhook endpoint
   - **Events**: Select the following:
     - Issue → Label added
     - Project → Label added
   - **Team filter**: Select your team (optional)

### Step 3: Webhook Payload Routing

You'll need a webhook router to dispatch to different CI jobs based on the payload. Options:

#### Option A: Custom Webhook Router

Create a simple service that:
1. Receives Linear webhook
2. Parses payload to determine label
3. Triggers appropriate Woodpecker job

Example (Node.js/Express):

```javascript
app.post('/linear-webhook', (req, res) => {
  const { action, data, type } = req.body;

  if (action !== 'create' || type !== 'IssueLabel') {
    return res.sendStatus(200);
  }

  const labelName = data.label?.name;
  const isProject = data.issue?.project !== undefined;

  let pipeline;
  switch (labelName) {
    case 'ai:plan':
      if (isProject) pipeline = 'plan-project';
      break;
    case 'ai:tasks':
      if (isProject) pipeline = 'generate-tasks';
      break;
    case 'ai:ready':
      pipeline = 'implement-issue';
      break;
    case 'ai:retry':
      pipeline = 'retry-issue';
      break;
    default:
      return res.sendStatus(200);
  }

  if (pipeline) {
    triggerWoodpeckerPipeline(pipeline, req.body);
  }

  res.sendStatus(200);
});
```

#### Option B: Woodpecker Custom Event

Configure Woodpecker to accept custom events and route internally:

```yaml
# In .woodpecker.yml
when:
  - event: custom
    evaluate: 'CI_CUSTOM_PAYLOAD contains "ai:plan"'
```

### Step 4: Test Linear Webhook

1. Add `ai:plan` label to a test Project
2. Check webhook delivery in Linear (Settings → Webhooks → Recent deliveries)
3. Verify Woodpecker receives and processes the event

## GitHub Webhook Configuration

### Step 1: Create GitHub Webhook

1. Go to your repository → Settings → Webhooks
2. Click "Add webhook"
3. Configure:
   - **Payload URL**: Your Woodpecker endpoint
   - **Content type**: `application/json`
   - **Secret**: Generate a secure secret
   - **Events**: Select:
     - Pull request reviews
   - **Active**: ✓

### Step 2: Configure Woodpecker for PR Reviews

The `address-feedback.yml` job triggers on:
- Built-in `pull_request` event with `review_requested_changes` action
- Custom webhook event from GitHub

### Step 3: Test GitHub Webhook

1. Create a test PR
2. Request changes in a review
3. Verify webhook delivery in GitHub (Settings → Webhooks → Recent deliveries)
4. Check Woodpecker for triggered job

## Payload Examples

### Linear Label Added (Project)

```json
{
  "action": "create",
  "type": "IssueLabel",
  "data": {
    "id": "label-instance-uuid",
    "label": {
      "id": "label-uuid",
      "name": "ai:plan"
    },
    "issue": {
      "id": "project-uuid",
      "identifier": "TIM-P-001",
      "title": "User Authentication"
    }
  },
  "organizationId": "org-uuid",
  "webhookTimestamp": 1234567890
}
```

### Linear Label Added (Issue)

```json
{
  "action": "create",
  "type": "IssueLabel",
  "data": {
    "id": "label-instance-uuid",
    "label": {
      "id": "label-uuid",
      "name": "ai:ready"
    },
    "issue": {
      "id": "issue-uuid",
      "identifier": "TIM-123",
      "title": "[T001] Create User model"
    }
  },
  "organizationId": "org-uuid",
  "webhookTimestamp": 1234567890
}
```

### GitHub PR Review (Changes Requested)

```json
{
  "action": "submitted",
  "review": {
    "id": 12345,
    "state": "changes_requested",
    "body": "Please fix the type error on line 42"
  },
  "pull_request": {
    "number": 123,
    "title": "TIM-123: Create User model",
    "head": {
      "ref": "issue-TIM-123-user-model"
    }
  },
  "repository": {
    "full_name": "your-org/your-repo"
  }
}
```

## Webhook Security

### Linear Webhook Verification

Linear webhooks include a signature header for verification:

```python
import hmac
import hashlib

def verify_linear_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

### GitHub Webhook Verification

```python
def verify_github_webhook(payload, signature, secret):
    expected = 'sha256=' + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

## Troubleshooting

### Webhook not received

1. Check webhook URL is accessible from internet
2. Verify firewall allows incoming connections
3. Check for SSL/TLS certificate issues
4. Review webhook delivery logs in Linear/GitHub

### Webhook received but job not triggered

1. Verify event type matches Woodpecker `when` conditions
2. Check payload parsing in router
3. Verify Woodpecker API token is valid
4. Check job configuration in `.woodpecker/` files

### Job triggered but fails

1. Check job logs for errors
2. Verify secrets are configured
3. Ensure CI image is available
4. Check network access to Linear/GitHub APIs

## Advanced: Webhook Relay Services

For development or if your CI is behind a firewall:

- **ngrok**: `ngrok http 8000`
- **smee.io**: `npx smee -u https://smee.io/xxx -p 8000`
- **Webhook.site**: For debugging payloads

## Monitoring and Alerts

Consider setting up:

1. **Webhook failure alerts**: Monitor for failed deliveries
2. **Job failure notifications**: Alert on CI failures
3. **Latency monitoring**: Track webhook-to-job latency
4. **Audit logging**: Log all webhook events for debugging

## Rate Limits

Be aware of rate limits:

- **Linear API**: 3600 requests per hour per token
- **GitHub API**: 5000 requests per hour per token
- **Woodpecker**: Varies by installation

Implement backoff strategies for high-volume workflows.
