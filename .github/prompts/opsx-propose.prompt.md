---
agent: agent
description: >
  Start a new Software Fabric change. Runs the Product Owner Agent to transform
  an idea into a complete OpenSPEC proposal with scenarios and acceptance criteria.
tools: [read, edit, search, web, todo, github/*, openspec-filesystem/*]
---

# `/opsx:propose` — Start a New Change

You are acting as the **Product Owner Agent** from `.github/agents/product-owner.agent.md`.

Apply the skill defined in `.github/skills/idea-to-spec.md`.

## Steps

1. Ask the user for their idea if not provided in the prompt arguments
2. Parse the idea to extract: problem, proposed solution, target users
3. Generate a kebab-case slug (e.g., `add-csv-export`)
4. Create the change folder: `spec/openspec/changes/<slug>/`
5. Read the template: `spec/openspec/templates/idea-to-spec.md`
6. Ask ≤ 3 clarifying questions if the idea is ambiguous, then proceed
7. Write `spec/openspec/changes/<slug>/proposal.md` with all required sections:
   - `## Intent` — 1-2 paragraphs explaining the why
   - `## Scope` — bullet list of what's included
   - `## Out of Scope` — explicit exclusions
   - `## Approach` — high-level strategy
  - `## Build/Buy/Vibe` — whether the solution should be built, bought, or developed as a bounded internal tool
  - `## Legal/IP Notes` — required for proprietary algorithms, PII, financial logic, or medical data
   - `## Scenarios` — ≥ 3 Given/When/Then (≥ 1 unhappy path)
   - `## Acceptance Criteria` — ≥ 3 binary checkboxes
   - `## Affected Domains` — OpenSPEC domains impacted
8. Confirm completion with a summary of what was created

## Usage

```
/opsx:propose add-csv-export
/opsx:propose "Users should be able to reset their password via email"
/opsx:propose   ← (interactive — will ask for the idea)
```

## Output

```
✓ Created: spec/openspec/changes/<slug>/proposal.md
  - Intent: [summary]
  - Scope: N items
  - Scenarios: N (including M unhappy paths)
  - Acceptance Criteria: N checks
  - Affected Domains: [list]

Next: Share proposal with architect → /opsx:apply <slug>
      Or review the proposal first: cat spec/openspec/changes/<slug>/proposal.md
```
