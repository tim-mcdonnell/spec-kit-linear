---
description: Identify underspecified areas in the Linear Project specification by asking up to 5 highly targeted clarification questions and updating the Project content.
handoffs:
  - label: Build Technical Plan
    agent: speckit.plan
    prompt: Create a plan for the spec. I am building with...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Goal: Detect and reduce ambiguity or missing decision points in the active Linear Project specification and record the clarifications directly in the Project's `content` field.

Note: This clarification workflow is expected to run (and be completed) BEFORE adding the `ai:plan` label. If the user explicitly states they are skipping clarification (e.g., exploratory spike), you may proceed, but must warn that downstream rework risk increases.

### Execution Steps

1. **Load the Linear Project**:

   The user must provide the Project identifier or URL. Parse it to get the project ID.

   ```graphql
   query GetProject($id: String!) {
     project(id: $id) {
       id
       name
       identifier
       content
       description
       url
     }
   }
   ```

   If the Project cannot be found, instruct user to run `/speckit.specify` first or provide a valid project identifier.

2. **Analyze the specification**: Perform a structured ambiguity & coverage scan using this taxonomy. For each category, mark status: Clear / Partial / Missing. Produce an internal coverage map used for prioritization.

   **Functional Scope & Behavior:**
   - Core user goals & success criteria
   - Explicit out-of-scope declarations
   - User roles / personas differentiation

   **Domain & Data Model:**
   - Entities, attributes, relationships
   - Identity & uniqueness rules
   - Lifecycle/state transitions
   - Data volume / scale assumptions

   **Interaction & UX Flow:**
   - Critical user journeys / sequences
   - Error/empty/loading states
   - Accessibility or localization notes

   **Non-Functional Quality Attributes:**
   - Performance (latency, throughput targets)
   - Scalability (horizontal/vertical, limits)
   - Reliability & availability (uptime, recovery expectations)
   - Observability (logging, metrics, tracing signals)
   - Security & privacy (authN/Z, data protection, threat assumptions)
   - Compliance / regulatory constraints (if any)

   **Integration & External Dependencies:**
   - External services/APIs and failure modes
   - Data import/export formats
   - Protocol/versioning assumptions

   **Edge Cases & Failure Handling:**
   - Negative scenarios
   - Rate limiting / throttling
   - Conflict resolution (e.g., concurrent edits)

   **Constraints & Tradeoffs:**
   - Technical constraints (language, storage, hosting)
   - Explicit tradeoffs or rejected alternatives

   **Terminology & Consistency:**
   - Canonical glossary terms
   - Avoided synonyms / deprecated terms

   **Completion Signals:**
   - Acceptance criteria testability
   - Measurable Definition of Done style indicators

   **Misc / Placeholders:**
   - TODO markers / unresolved decisions
   - Ambiguous adjectives ("robust", "intuitive") lacking quantification

   For each category with Partial or Missing status, add a candidate question opportunity unless:
   - Clarification would not materially change implementation or validation strategy
   - Information is better deferred to planning phase (note internally)

3. **Generate prioritized questions** (internally):
   - Maximum of 5 total questions across the session
   - Each question must be answerable with EITHER:
     - A short multiple-choice selection (2-5 distinct, mutually exclusive options), OR
     - A one-word / short-phrase answer (explicitly constrain: "Answer in <=5 words")
   - Only include questions whose answers materially impact architecture, data modeling, task decomposition, test design, UX behavior, operational readiness, or compliance validation
   - Favor clarifications that reduce downstream rework risk or prevent misaligned acceptance tests
   - If more than 5 categories remain unresolved, select the top 5 by (Impact × Uncertainty) heuristic

4. **Sequential questioning loop** (interactive):

   - Present EXACTLY ONE question at a time
   - For multiple-choice questions:
     - **Analyze all options** and determine the **most suitable option** based on best practices, common patterns, risk reduction
     - Present your **recommended option prominently** at the top with clear reasoning
     - Format as: `**Recommended:** Option [X] - <reasoning>`
     - Then render all options as a Markdown table:

       | Option | Description |
       |--------|-------------|
       | A | <Option A description> |
       | B | <Option B description> |
       | C | <Option C description> |
       | Short | Provide a different short answer (<=5 words) |

     - Add: `Reply with the option letter, "yes" to accept recommendation, or provide your own answer.`

   - For short-answer style (no meaningful discrete options):
     - Provide your **suggested answer** based on best practices
     - Format as: `**Suggested:** <your proposed answer> - <brief reasoning>`
     - Then output: `Format: Short answer (<=5 words). Say "yes" to accept, or provide your own.`

   - After the user answers:
     - If user replies "yes" or "recommended" or "suggested", use your stated recommendation
     - Otherwise, validate the answer maps to one option or fits the <=5 word constraint
     - If ambiguous, ask for quick disambiguation (does not count as new question)
     - Once satisfactory, record it in working memory

   - Stop asking further questions when:
     - All critical ambiguities resolved early
     - User signals completion ("done", "good", "no more")
     - You reach 5 asked questions

   - Never reveal future queued questions in advance
   - If no valid questions exist at start, immediately report no critical ambiguities

5. **Update the Project content** after EACH accepted answer:

   - Maintain in-memory representation of the spec content
   - For the first integrated answer in this session:
     - Ensure a `## Clarifications` section exists (create if missing)
     - Under it, create `### Session YYYY-MM-DD` subheading for today
   - Append a bullet line immediately after acceptance: `- Q: <question> → A: <final answer>`
   - Then apply the clarification to the most appropriate section:
     - Functional ambiguity → Update Functional Requirements
     - User interaction → Update User Stories or Actors
     - Data shape → Update Data Model
     - Non-functional constraint → Add measurable criteria to Quality Attributes
     - Edge case → Add to Edge Cases / Error Handling
     - Terminology conflict → Normalize term across spec
   - If the clarification invalidates an earlier ambiguous statement, replace it
   - Update Linear Project content after each integration:

     ```graphql
     mutation UpdateProject($id: String!, $input: ProjectUpdateInput!) {
       projectUpdate(id: $id, input: $input) {
         project { id content }
         success
       }
     }
     ```

6. **Validation** (performed after EACH update plus final pass):
   - Clarifications session contains exactly one bullet per accepted answer
   - Total asked (accepted) questions ≤ 5
   - Updated sections contain no lingering vague placeholders
   - No contradictory earlier statement remains
   - Markdown structure valid
   - Terminology consistency: same canonical term used across all updated sections

7. **Report completion** (after questioning loop ends or early termination):
   - Number of questions asked & answered
   - Linear Project URL (for reference)
   - Sections touched (list names)
   - Coverage summary table listing each taxonomy category with Status:
     - **Resolved**: Was Partial/Missing and addressed
     - **Deferred**: Exceeds question quota or better suited for planning
     - **Clear**: Already sufficient
     - **Outstanding**: Still Partial/Missing but low impact
   - If any Outstanding or Deferred remain, recommend whether to proceed to `ai:plan` label or run `/speckit.clarify` again
   - Suggested next step: "Add the `ai:plan` label to the Project when ready for planning phase"

### Behavior Rules

- If no meaningful ambiguities found, respond: "No critical ambiguities detected worth formal clarification." and suggest proceeding
- If Project not found, instruct user to run `/speckit.specify` first
- Never exceed 5 total asked questions
- Avoid speculative tech stack questions unless the absence blocks functional clarity
- Respect user early termination signals ("stop", "done", "proceed")
- If no questions asked due to full coverage, output a compact coverage summary then suggest advancing

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
  }
}
```

### Update Project Content
```graphql
mutation UpdateProject($id: String!, $input: ProjectUpdateInput!) {
  projectUpdate(id: $id, input: $input) {
    project { id content }
    success
  }
}
```

Context for prioritization: {ARGS}
