---
name: fabric-propose
description: Start Software Fabric planning while preserving its intake, approval, and persona handoffs.
license: MIT
compatibility: Requires Python, Node.js 26 or later, and OpenSpec 1.16.0.
metadata:
  author: agentic-shared
  
---

# Fabric proposal and planning

## Purpose and trigger

Use this entry point for a new Fabric-managed change. Existing Fabric
consumers remain in Fabric mode unless the user explicitly selects standalone
OpenSpec for the current work. In standalone mode, use the upstream OpenSpec
workflow instead; repository merge and release controls still apply.

## Workflow

1. Resolve the advisory route with
   `python .github/skills/fabric-propose/scripts/route_fabric_workflow.py --action propose`.
   For an explicit standalone selection, append `--mode standalone`, use
   `openspec-propose` unchanged, and do not perform the Fabric steps below.
   Otherwise run the compatibility checker at
   `.github/skills/software-fabric-kickoff/scripts/check_openspec_compatibility.py`
   and resolve the selected root with `openspec context --json`. Stop and
   report any failure; do not initialize or create files implicitly.
2. Follow the Pre-Capture Intake Decision in
   `.github/instructions/fabric-workflow.instructions.md`. An explicit
   request to create named artifacts counts as Proceed, not acceptance.
   Deferred or rejected intake makes no repository changes.
3. Use the `idea-to-spec` skill to scaffold the change and prepare the
   proposal using OpenSpec CLI status and artifact instructions. Preserve
   selected-store flags on every applicable command.
4. Present the proposal and obtain explicit acceptance before design. Determine
   UX applicability from accepted scope. Visual work goes through `ux-design`;
   nonvisual work goes directly to architecture.
5. After acceptance, use `spec-to-design` to prepare delta specs, design, and
   ordered tasks. Required Fabric planning roles cannot be waived by a
   skipped OpenSpec artifact.
6. Present the completed plan for review and stop. A separate explicit
   acceptance of the current proposal/spec and implementation request are
   required before Fabric apply.

The primary non-developer intake is a GitHub issue labelled `idea`; retain its
title, fields, discussion, and `stage:proposal` until approval. Direct
`/fabric-propose <description>` is a valid alternative without an issue.
This entry point is planning only: Do not edit project code.

## Quality checks and output

- Report the selected change and root, created artifacts, and any blocker.
- Preserve testing, security, applicable legal, review, and archive gates.
- Do not claim that OpenSpec CLI readiness proves Fabric acceptance or gate
  clearance.

## Errors and handoff

If compatibility, root resolution, required planning, or acceptance is
unavailable, report the specific blocker and stop without bypassing it. Hand an
accepted nonvisual proposal to the Architect; hand an accepted visual
proposal to UX before architecture. The completed plan is handed to the
requester for review, not directly to implementation.
