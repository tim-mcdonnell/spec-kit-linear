---
description: Create a Linear Project with the feature specification stored in the Project's content field.
handoffs:
  - label: Build Technical Plan
    agent: speckit.plan
    prompt: Create a plan for the spec. I am building with...
  - label: Clarify Spec Requirements
    agent: speckit.clarify
    prompt: Clarify specification requirements
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/speckit.specify` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `{ARGS}` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature description, do this:

1. **Generate a concise project name** (2-6 words) for the Linear Project:
   - Analyze the feature description and extract the most meaningful keywords
   - Create a descriptive name that captures the essence of the feature
   - Use title case (e.g., "User Authentication System", "Payment Processing Integration")
   - Preserve technical terms and acronyms (OAuth2, API, JWT, etc.)
   - Examples:
     - "I want to add user authentication" → "User Authentication"
     - "Implement OAuth2 integration for the API" → "OAuth2 API Integration"
     - "Create a dashboard for analytics" → "Analytics Dashboard"
     - "Fix payment processing timeout bug" → "Payment Timeout Fix"

2. **Load configuration and verify Linear connection**:
   - Check for `LINEAR_TOKEN` environment variable
   - Load `linear-config.json` from the project root
   - Verify the team ID is configured
   - If configuration is missing, guide user to run `specify linear-setup`

3. **Check for existing projects** (using Linear GraphQL):
   ```graphql
   query SearchProjects($query: String!) {
     projectSearch(query: $query) {
       nodes { id name status { name } }
     }
   }
   ```
   - Search for projects with similar names
   - If a matching project exists:
     - Ask user if they want to update the existing project or create a new one
     - If updating, proceed with update mutation instead of create

4. **Generate the specification** following this flow:
   1. Parse user description from Input
      If empty: ERROR "No feature description provided"
   2. Extract key concepts from description
      Identify: actors, actions, data, constraints
   3. For unclear aspects:
      - Make informed guesses based on context and industry standards
      - Only mark with [NEEDS CLARIFICATION: specific question] if:
        - The choice significantly impacts feature scope or user experience
        - Multiple reasonable interpretations exist with different implications
        - No reasonable default exists
      - **LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers total**
      - Prioritize clarifications by impact: scope > security/privacy > user experience > technical details
   4. Generate User Scenarios & Testing section
      If no clear user flow: ERROR "Cannot determine user scenarios"
   5. Generate Functional Requirements
      Each requirement must be testable
      Use reasonable defaults for unspecified details (document assumptions in Assumptions section)
   6. Define Success Criteria
      Create measurable, technology-agnostic outcomes
   7. Identify Key Entities (if data involved)
   8. Format as Markdown for the Project's `content` field

5. **Create the Linear Project** (using GraphQL mutation):
   ```graphql
   mutation CreateProject($input: ProjectCreateInput!) {
     projectCreate(input: $input) {
       project { id name identifier url }
       success
     }
   }
   ```
   Input:
   - `teamIds`: [Team ID from config]
   - `name`: Generated project name
   - `description`: One-line summary of the feature
   - `content`: Full specification in Markdown format

6. **Specification Quality Validation**: After creating the project:

   a. **Validate against quality criteria**:
      - No implementation details (languages, frameworks, APIs)
      - Focused on user value and business needs
      - Written for non-technical stakeholders
      - All mandatory sections completed
      - Requirements are testable and unambiguous
      - Success criteria are measurable and technology-agnostic
      - No excessive [NEEDS CLARIFICATION] markers (max 3)

   b. **Handle Validation Results**:

      - **If [NEEDS CLARIFICATION] markers remain**:
        1. Extract all [NEEDS CLARIFICATION: ...] markers from the spec
        2. Present each as a question with multiple choice options:

           ```markdown
           ## Question [N]: [Topic]

           **Context**: [Quote relevant spec section]

           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]

           **Suggested Answers**:

           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |

           **Your choice**: _[Wait for user response]_
           ```

        3. After user responds, update the Project content via GraphQL:
           ```graphql
           mutation UpdateProject($id: String!, $input: ProjectUpdateInput!) {
             projectUpdate(id: $id, input: $input) {
               project { id content }
               success
             }
           }
           ```

7. **Report completion** with:
   - Linear Project URL
   - Project identifier (e.g., "TIM-P-001")
   - Summary of the specification
   - Validation status
   - Suggested next step: "Add the `ai:plan` label when ready for planning phase" or `/speckit.clarify` if clarifications remain

**NOTE:** The specification is stored in Linear's `content` field. All artifacts will be in Linear - no local files are created.

## General Guidelines

### Quick Guidelines

- Focus on **WHAT** users need and **WHY**.
- Avoid HOW to implement (no tech stack, APIs, code structure).
- Written for business stakeholders, not developers.

### For AI Generation

When creating this spec from a user prompt:

1. **Make informed guesses**: Use context, industry standards, and common patterns to fill gaps
2. **Document assumptions**: Record reasonable defaults in the Assumptions section
3. **Limit clarifications**: Maximum 3 [NEEDS CLARIFICATION] markers - use only for critical decisions
4. **Prioritize clarifications**: scope > security/privacy > user experience > technical details
5. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" test

**Examples of reasonable defaults** (don't ask about these):

- Data retention: Industry-standard practices for the domain
- Performance targets: Standard web/mobile app expectations unless specified
- Error handling: User-friendly messages with appropriate fallbacks
- Authentication method: Standard session-based or OAuth2 for web apps
- Integration patterns: RESTful APIs unless specified otherwise

### Success Criteria Guidelines

Success criteria must be:

1. **Measurable**: Include specific metrics (time, percentage, count, rate)
2. **Technology-agnostic**: No mention of frameworks, languages, databases, or tools
3. **User-focused**: Describe outcomes from user/business perspective
4. **Verifiable**: Can be tested/validated without knowing implementation details

**Good examples**:

- "Users can complete checkout in under 3 minutes"
- "System supports 10,000 concurrent users"
- "95% of searches return results in under 1 second"

**Bad examples** (implementation-focused):

- "API response time is under 200ms"
- "Database can handle 1000 TPS"
- "React components render efficiently"

## Linear API Reference

### Create Project
```graphql
mutation CreateProject($input: ProjectCreateInput!) {
  projectCreate(input: $input) {
    project {
      id
      name
      identifier
      url
    }
    success
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

### Search Projects
```graphql
query SearchProjects($query: String!) {
  projectSearch(query: $query) {
    nodes { id name status { name } }
  }
}
```
