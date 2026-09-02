---
name: openspec-apply-change
description: Implement and validate tasks from an OpenSpec change. Use when the user wants to start or continue implementation. Do not bypass planning artifacts, gates, or task-scope constraints.
allowed-tools: Bash(openspec:*)
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.11.0"
---

Implement tasks from an OpenSpec change.

Node.js 26 or later and the OpenSpec CLI are required. Run `openspec --version` and
`openspec context --json` before changing artifacts or implementation code. If either
command fails, stop and provide the installation and initialization commands. Do not fall back to a legacy prompt workflow.

Do not mark partial or deferred work complete; mark a task complete only after its
specified behavior is fully implemented and validated.

**Store selection:** If the user names a store (a store is a standalone OpenSpec repo registered on this machine) or the work lives in one, run `openspec store list --json` to discover registered store ids, then pass `--store <id>` on the commands that read or write specs and changes (`new change`, `status`, `instructions`, `list`, `show`, `validate`, `archive`, `doctor`, `context`, `schemas`, `view`). Once selected, treat `--store <id>` as sticky for the rest of the workflow. Every unscoped example of those commands below is shorthand: before running it, append the flag. For example, run `openspec status --change "<name>" --json --store "<id>"`, not the unscoped form shown below. Other commands do not take the flag. Hints printed by commands already carry the flag; keep it on follow-ups. Without a store, commands act on the nearest local `openspec/` root.

**Input**: Optionally specify a change name (e.g., `/opsx-apply add-auth`). If omitted, check if it can be inferred from conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one change exists that is not yet archived and has remaining tasks
   - If ambiguous, run `openspec list --json` to get available changes and ask the user to select one

   Always announce: "Using change: <name>" and how to override (e.g., `/opsx-apply <other>`).

2. **Check status to understand the schema**
   ```bash
   openspec status --change "<name>" --json
   ```
   Parse the JSON to understand:
   - `schemaName`: The workflow being used (e.g., "spec-driven")
   - `planningHome`, `changeRoot`, and `actionContext`: planning scope and edit constraints
   - Which artifact contains the tasks (typically "tasks" for spec-driven, check status for others)

   If the JSON output cannot be parsed, stop and report the raw CLI output to the user rather than guessing its structure.

3. **Get apply instructions**

   ```bash
   openspec instructions apply --change "<name>" --json
   ```

   This returns:
   - `contextFiles`: artifact ID -> array of concrete file paths (varies by schema - could be proposal/specs/design/tasks or spec/tests/implementation/docs)
   - Progress (total, complete, remaining)
   - Task list with status
   - Dynamic instruction based on current state
   - Optional `context`: current required project instruction input from the selected root
   - Optional `operationGuidance`: current advisory guidance for apply

   **Handle states:**
   - If `state: "blocked"` (missing artifacts): show message, suggest using `/opsx-continue` (if it is not installed, run `openspec status --change "<name>" --json` to see the next artifact and `openspec instructions <artifact-id> --change "<name>" --json` for how to create it)
   - If `state: "all_done"`: congratulate, suggest archive
   - Otherwise: proceed to implementation

   Use this decision table for `context` and `operationGuidance`:

   | Input | Required/Optional | Action on conflict with built-in instruction, explicit user choice, or CLI-controlled value | Prohibited |
   |---|---|---|---|
   | `context` | Required: read and apply relevant project facts, conventions, and constraints while implementing | Report the conflict and preserve the controlling value | Not evidence of task completion; do not copy verbatim into implementation files or planning artifacts; does not permit bypassing a blocked state |
   | `operationGuidance` | Optional: read every entry, follow entries that are applicable and compatible with the built-in workflow | Do not follow the conflicting entry and explain why | Not evidence of task completion; do not copy verbatim into implementation files or planning artifacts; does not permit bypassing a blocked state |

   Keep both fields separate from CLI-returned state, missing artifacts, tasks,
   progress, `contextFiles`, and the built-in `instruction`. These are
   prompt-level behavior contracts, not enforceable checks.

4. **Read context files**

   Read every file path listed under `contextFiles` from the apply instructions output.
   The files depend on the schema being used:
   - **spec-driven**: proposal, specs, design, tasks
   - Other schemas: follow the contextFiles from CLI output

   If a file listed in contextFiles does not exist, report this as a blocker and stop before implementing tasks.

   Do not copy `context` or `operationGuidance` verbatim into implementation
   files or planning artifacts unless the user separately asks for that content.

5. **Show current progress**

   Display:
   - Schema being used
   - Progress: "N/M tasks complete"
   - Remaining tasks overview
   - Dynamic instruction from CLI

6. **Implement tasks (loop until done or blocked)**

   For each pending task:
   - Show which task is being worked on
   - Make the code changes required
   - Keep changes minimal and focused
   - Mark task complete in the tasks file: `- [ ]` → `- [x]`. If the schema uses a different task-marking format, use the format shown in the tasks artifact instead of assuming markdown checkboxes.
   - Continue to next task

   **Pause if:**
   - Task is unclear → ask for clarification
   - Implementation reveals a design issue → suggest updating artifacts
   - A task needs work beyond what the spec and tasks describe, or you are tempted to drop, narrow, defer, or accept exceptions to specified behavior to make it fit → surface the added scope and ask; do not absorb it silently
   - Error or blocker encountered → report and wait for guidance
   - User interrupts

7. **On completion or pause, show status**

   Display:
   - Tasks completed this session
   - Overall progress: "N/M tasks complete"
   - If all done: suggest archive
   - If paused: explain why and wait for guidance

**Output During Implementation**

```
## Implementing: <change-name> (schema: <schema-name>)

Working on task 3/7: <task description>
[...implementation happening...]
✓ Task complete

Working on task 4/7: <task description>
[...implementation happening...]
✓ Task complete
```

**Output On Completion**

```
## Implementation Complete

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 7/7 tasks complete ✓

### Completed This Session
- [x] Task 1
- [x] Task 2
...

All tasks complete! You can archive this change with `/opsx-archive`.
```

**Output On Pause (Issue Encountered)**

```
## Implementation Paused

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 4/7 tasks complete

### Issue Encountered
<description of the issue>

**Options:**
1. <option 1>
2. <option 2>
3. Other approach

What would you like to do?
```

**Guardrails**
- Keep going through tasks until done or blocked
- Always read context files before starting (from the apply instructions output)
- If task is ambiguous, pause and ask before implementing
- If implementation reveals issues, pause and suggest artifact updates
- Keep code changes minimal and scoped to each task
- Update task checkbox immediately after completing each task
- Pause on errors, blockers, or unclear requirements - don't guess
- When a task needs work beyond what the spec describes, surface the added scope and pause - never silently narrow, defer, or simplify away specified behavior
- Only mark a task `- [x]` when its specified behavior is fully implemented, not when it is partially done or deferred
- Use contextFiles from CLI output, don't assume specific file names
- Do not use context or operation guidance as proof that a task is complete
- Apply relevant project context; report conflicts with controlling workflow inputs
- Consider every guidance entry; explain any inapplicable or conflicting advice
- Do not copy runtime context or operation guidance into implementation files or planning artifacts
- Preserve CLI-controlled blocked/ready/all-done behavior and completion criteria

**Fluid Workflow Integration**

This skill supports the "actions on a change" model:

- **Can be invoked anytime**: Before all artifacts are done (if tasks exist), after partial implementation, interleaved with other actions
- **Allows artifact updates**: If implementation reveals design issues, suggest updating artifacts - not phase-locked, work fluidly

## When to Use & Triggers

Use when a selected change has a ready `tasks.md` and implementation is explicitly requested. Do not use for proposal or design authoring.

## Workflows & Steps

1. Select the change and read CLI status and context files.
2. Implement one pending task, validate it, and mark it complete.
3. Continue until complete or stop on a blocker.

## Scripts & Tools

- Run the OpenSpec version, context, status, and apply-instruction commands before editing.
- Use the exact context files returned by the CLI.

## Rules & Guidelines

- Implement only approved tasks and mark them complete only after validation.
- Stop on ambiguity, missing artifacts, failed gates, or scope expansion.

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| CLI unavailable | OpenSpec is not installed or initialized | Report setup requirements and stop |
| Missing context file | Required artifact is absent | Report the blocker and stop |
| Validation failure | Behavior is incomplete or incorrect | Repair the same task and rerun validation |

## Scenarios & References

- Use proposal, delta specs, design, tasks, and repository instructions as the implementation contract.
- Preserve scenario behavior and required test, security, legal, and operations handoffs.

## Quick Reference

| Task | Action |
|---|---|
| Start | Read CLI status and apply instructions |
| Implement | Work one pending task at a time |
| Finish | Validate, update task status, and report evidence |

## Collaboration & Iteration Loop

- Report progress after each validated task and surface blockers immediately.
- Feed implementation failures back into change artifacts instead of silently narrowing scope.

## Output Specs, Success, Evaluation & Security

- Output completed tasks, remaining tasks, validation evidence, and blockers.
- Success requires specified behavior and gates to pass without exposing secrets.
