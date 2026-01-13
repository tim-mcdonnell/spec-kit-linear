---
description: Perform a non-destructive cross-artifact consistency and quality analysis across the Linear Project spec, Plan Issue, and task Issues after task generation.
handoffs:
  - label: Update Specification
    agent: speckit.specify
    prompt: Update the specification to address the issues found
  - label: Update Plan
    agent: speckit.plan
    prompt: Update the plan to address the issues found
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The input should include the Project identifier.

## Goal

Identify inconsistencies, duplications, ambiguities, and underspecified items across the three core artifacts (Project spec, Plan Issue, task Issues) before implementation. This command MUST run only after `/speckit.tasks` has successfully created Milestones and Issues.

## Operating Constraints

**STRICTLY READ-ONLY**: Do **not** modify any Linear artifacts. Output a structured analysis report. Offer an optional remediation plan (user must explicitly approve before any follow-up editing commands would be invoked manually).

**Constitution Authority**: The project constitution (`/memory/constitution.md`) is **non-negotiable** within this analysis scope. Constitution conflicts are automatically CRITICAL and require adjustment of the spec, plan, or tasks—not dilution, reinterpretation, or silent ignoring of the principle. If a principle itself needs to change, that must occur in a separate, explicit constitution update outside `/speckit.analyze`.

## Execution Steps

### 1. Initialize Analysis Context

Load the Linear Project and its associated artifacts:

```graphql
query GetProjectForAnalysis($id: String!) {
  project(id: $id) {
    id
    name
    identifier
    content
    url
    projectMilestones {
      nodes { id name description sortOrder }
    }
    issues {
      nodes {
        id
        identifier
        title
        description
        state { name }
        projectMilestone { id name }
        priority
        comments { nodes { id body createdAt } }
      }
    }
  }
}
```

- Parse Project ID from user input
- Load `linear-config.json` for team/label configuration
- Find the Plan Issue (title starts with "Plan:")
- Abort with an error message if Project not found or Plan Issue is missing

### 2. Load Artifacts (Progressive Disclosure)

Load only the minimal necessary context from each artifact:

**From Project `content` field (spec):**

- Overview/Context
- Functional Requirements
- Non-Functional Requirements
- User Stories
- Edge Cases (if present)

**From Plan Issue and its comments:**

- Architecture/stack choices
- Data Model references
- Phases
- Technical constraints

**From task Issues:**

- Issue IDs/identifiers
- Titles and descriptions
- Milestone grouping (phases)
- Priority levels
- Blocking relations

**From constitution:**

- Load `/memory/constitution.md` for principle validation

### 3. Build Semantic Models

Create internal representations (do not include raw artifacts in output):

- **Requirements inventory**: Each functional + non-functional requirement with a stable key (derive slug based on imperative phrase; e.g., "User can upload file" → `user-can-upload-file`)
- **User story/action inventory**: Discrete user actions with acceptance criteria
- **Task coverage mapping**: Map each Issue to one or more requirements or stories (inference by keyword / explicit reference patterns like IDs or key phrases)
- **Constitution rule set**: Extract principle names and MUST/SHOULD normative statements

### 4. Detection Passes (Token-Efficient Analysis)

Focus on high-signal findings. Limit to 50 findings total; aggregate remainder in overflow summary.

#### A. Duplication Detection

- Identify near-duplicate requirements
- Mark lower-quality phrasing for consolidation

#### B. Ambiguity Detection

- Flag vague adjectives (fast, scalable, secure, intuitive, robust) lacking measurable criteria
- Flag unresolved placeholders (TODO, TKTK, ???, `<placeholder>`, etc.)

#### C. Underspecification

- Requirements with verbs but missing object or measurable outcome
- User stories missing acceptance criteria alignment
- Issues referencing files or components not defined in spec/plan

#### D. Constitution Alignment

- Any requirement or plan element conflicting with a MUST principle
- Missing mandated sections or quality gates from constitution

#### E. Coverage Gaps

- Requirements with zero associated Issues
- Issues with no mapped requirement/story
- Non-functional requirements not reflected in Issues (e.g., performance, security)

#### F. Inconsistency

- Terminology drift (same concept named differently across artifacts)
- Data entities referenced in plan but absent in spec (or vice versa)
- Issue ordering/blocking contradictions (e.g., integration issues before foundational setup without dependency note)
- Conflicting requirements (e.g., one requires Next.js while other specifies Vue)

### 5. Severity Assignment

Use this heuristic to prioritize findings:

- **CRITICAL**: Violates constitution MUST, missing core spec artifact, or requirement with zero coverage that blocks baseline functionality
- **HIGH**: Duplicate or conflicting requirement, ambiguous security/performance attribute, untestable acceptance criterion
- **MEDIUM**: Terminology drift, missing non-functional task coverage, underspecified edge case
- **LOW**: Style/wording improvements, minor redundancy not affecting execution order

### 6. Produce Compact Analysis Report

Output a Markdown report with the following structure:

## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Duplication | HIGH | Project spec §FR-001 | Two similar requirements ... | Merge phrasing; keep clearer version |

(Add one row per finding; generate stable IDs prefixed by category initial.)

**Coverage Summary Table:**

| Requirement Key | Has Issue? | Issue IDs | Notes |
|-----------------|------------|-----------|-------|

**Constitution Alignment Issues:** (if any)

**Unmapped Issues:** (if any)

**Metrics:**

- Total Requirements
- Total Issues
- Coverage % (requirements with >=1 Issue)
- Ambiguity Count
- Duplication Count
- Critical Findings Count

### 7. Provide Next Actions

At end of report, output a concise Next Actions block:

- If CRITICAL issues exist: Recommend resolving before `/speckit.implement`
- If only LOW/MEDIUM: User may proceed, but provide improvement suggestions
- Provide explicit command suggestions: e.g., "Run /speckit.specify to update the Project spec", "Run /speckit.plan to adjust architecture", "Create additional Issues to add coverage for 'performance-metrics'"

### 8. Offer Remediation

Ask the user: "Would you like me to suggest concrete remediation edits for the top N issues?" (Do NOT apply them automatically.)

## Operating Principles

### Context Efficiency

- **Minimal high-signal tokens**: Focus on actionable findings, not exhaustive documentation
- **Progressive disclosure**: Load artifacts incrementally; don't dump all content into analysis
- **Token-efficient output**: Limit findings table to 50 rows; summarize overflow
- **Deterministic results**: Rerunning without changes should produce consistent IDs and counts

### Analysis Guidelines

- **NEVER modify Linear artifacts** (this is read-only analysis)
- **NEVER hallucinate missing sections** (if absent, report them accurately)
- **Prioritize constitution violations** (these are always CRITICAL)
- **Use examples over exhaustive rules** (cite specific instances, not generic patterns)
- **Report zero findings gracefully** (emit success report with coverage statistics)

## Linear API Reference

### Get Project with All Artifacts
```graphql
query GetProjectForAnalysis($id: String!) {
  project(id: $id) {
    id
    name
    identifier
    content
    url
    projectMilestones {
      nodes { id name description sortOrder }
    }
    issues {
      nodes {
        id
        identifier
        title
        description
        state { name }
        projectMilestone { id name }
        priority
        labels { nodes { name } }
        relations {
          nodes {
            type
            relatedIssue { id identifier title }
          }
        }
        comments { nodes { id body createdAt } }
      }
    }
  }
}
```

## Key Rules

- All artifacts are in Linear (Project content, Plan Issue, task Issues)
- Use Issue identifiers (e.g., TIM-001) for references, not file paths
- Check blocking relations for dependency analysis
- Check Milestones for phase grouping
