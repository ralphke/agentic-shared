---
name: openspec-bulk-archive-change
description: Archive multiple completed OpenSpec changes at once. Use when archiving several parallel changes. Also use for a plural archive request - "openspec bulk-archive", "opsx bulk-archive", "openspec archive all", or "openspec archive these changes".
allowed-tools: Bash(openspec:*)
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.16.0"
---

Archive multiple completed changes in a single operation.

This skill allows you to batch-archive changes, handling spec conflicts intelligently by checking the codebase to determine what's actually implemented.

**Mandatory Fabric preflight:** Before any archive-driven sync writes or moves,
read `.github/instructions/openspec-workflow.instructions.md` and verify its
Mandatory Planning Contract and full Quality Gate Checklist for each change.
Required artifacts/tasks and every mandatory gate must be complete and verifiable.
User confirmation cannot override mandatory gates. Optional-artifact warnings
remain informative. A missing optional guidance lookup does not waive preflight.

**Store selection:** If the user names a store (a store is a standalone OpenSpec repo registered on this machine) or the work lives in one, run `openspec store list --json` to discover registered store ids, then pass `--store <id>` on the commands that read or write specs and changes (`new change`, `status`, `instructions`, `list`, `show`, `validate`, `archive`, `doctor`, `context`, `schemas`, `view`). Once selected, treat `--store <id>` as sticky for the rest of the workflow. Every unscoped example of those commands below is shorthand: before running it, append the flag. For example, run `openspec status --change "<name>" --json --store "<id>"`, not the unscoped form shown below. Other commands do not take the flag. Hints printed by commands already carry the flag; keep it on follow-ups. Without a store, commands act on the nearest local `openspec/` root.

**Project check:** These steps expect a project that already uses OpenSpec. Before the first step that writes anything (`new change`, `archive`, `sync specs`, or authoring an artifact file), confirm the project has a root: run `openspec list --json` (with `--store <id>` when a store is selected, since the store is then the root) and read `root`. A root object means the project is set up. `"root": null` means it is not - there is no `openspec/` directory here, and a write such as `openspec new change` would create one as a side effect. The command also exits non-zero, which is that answer rather than a broken CLI, so read the JSON instead of retrying or working around it.

One `"root": null` is not about setup: when a `status` error message starts with `Declared in` or `Invalid store declaration in` and names this project's `openspec/config.yaml` (or `config.yml`), the project does use OpenSpec through a store it declares, which this machine cannot resolve (the store is not registered, or the `store:` line is malformed). Do not treat it as uninitialized and skip the branches below: stop before writing and show the user that error's `message` and `fix`.

Otherwise, with no root, what happens next depends on how this workflow was reached:

- **Auto-selected**: you chose this workflow yourself, without the user naming OpenSpec, naming this skill, or running its slash command. Stop using OpenSpec and answer the request normally, as you would with no OpenSpec installed. Do not ask them to set anything up and do not mention OpenSpec setup.
- **Explicit OpenSpec request**: the user named OpenSpec, named this skill, or ran its slash command. Stop before writing and ask how to proceed: set this project up (`openspec init`), target a store they already have (`--store <id>`), or continue without OpenSpec for this request. Wait for their answer.

In both branches, never create the root as a side effect: do not run `openspec init` until the user asks for it, do not hand-create `openspec/` files, and do not let a command create it.

`<capability-path>` is the spec directory relative to `specs/` (for example, `user-auth` or `identity/user-auth`). Preserve the full path from each delta spec when resolving its main spec.

**Input**: None required (prompts for selection)

**Steps**

1. **Get active changes**

   Run `openspec list --json` to get all active changes.

   If no active changes exist, inform user and stop.

2. **Prompt for change selection**

   Ask the user to choose changes (multi-select):
   - Show each change name and task status from the list output
   - Include an option for "All changes"
   - Allow any number of selections (1+ works, 2+ is the typical use case)

   **IMPORTANT**: Do NOT auto-select. Always let the user choose.

   **Load current archive inputs once for the selected root before batch validation:**

   Choose one selected change from this root and run
   `openspec instructions archive --change "<selected-change>" --json` with the
   same selected-root flags. This lookup is advisory and optional: it only supplies
   extra prompt inputs, so it must never block the batch. If it fails or returns
   invalid JSON — for example on an older CLI that does not support this command
   yet — continue the batch with no context and no operation guidance. Do not
   report an error and do not stop.

   A valid response may omit `context` and `operationGuidance`. Treat
   `context` as a required prompt-level input across the batch: read and consider
   it, and apply relevant project facts, conventions, and constraints. Treat
   `operationGuidance` as optional additive advice: read and consider every
   entry, and follow entries that are applicable and compatible with the built-in
   batch workflow.

   Keep both fields separate from conflict analysis, explicit user choices,
   resolved paths, CLI checks, and command contracts. If context conflicts with one
   of those controlling inputs, report the conflict and preserve the controlling
   value. If guidance is inapplicable or conflicts with a controlling input, do not
   follow it and explain why. Do not infer skipped prompts, replacement paths, or
   flags from either field, and do not copy their text verbatim into specs, changes,
   or summaries. These are prompt-level behavior contracts, not enforceable checks.

3. **Batch validation - gather status for all selected changes**

   Run `openspec list --json` once with the same selected-root flags for task
   progress. If the lookup fails, returns invalid JSON, or omits any selected
   change, contains a duplicate selected change, or returns invalid counts,
   report the problem and stop before syncing or archiving the batch.

   For each selected change, collect:

   a. **Artifact status** - Run `openspec status --change "<name>" --json`
      - Parse `schemaName`, `artifacts`, `planningHome`, `changeRoot`, `artifactPaths`, and `actionContext`
      - Note which artifacts are `done` vs other states
      - Resolve required proposal, specs, design, and task roles and their
        transitive dependencies through returned schema paths. Missing,
        incomplete, skipped, or ambiguous required roles block the entire change.
        `skip_specs` is not a waiver; genuinely optional artifacts remain warnings.
      - Verify current proposal/spec acceptance and the full mandatory Quality
        Gate Checklist. Unmet or unverifiable evidence marks the change `Blocked`
        before any sync writes or moves. Leave blocked changes out of conflicts.

   b. **Task completion** - Find the `changes` entry from the list response whose `name` exactly matches this change
      - Require nonnegative integer `totalTasks` and `completedTasks`, with `completedTasks <= totalTasks`
      - Incomplete tasks = `totalTasks - completedTasks`
      - The CLI resolves the schema's tracked task files, including custom artifact names, output paths, and globs
      - Do not infer task completion from artifact status, an artifact id of `tasks`, or the absence of a top-level `tasks.md`
      - The CLI counts only `x`/`X` checkbox markers as complete; other markers remain incomplete
      - Incomplete tasks block the whole change. Zero counts alone do not prove
        completion: missing or empty required task tracking also blocks it.

   c. **Delta specs** - Check `artifactPaths.specs.existingOutputPaths` from status JSON
      - List which capability specs exist
      - For each, extract requirement names (lines matching `### Requirement: <name>`)
      - Treat this list as the only delta-spec source. If the `specs` entry is
        missing or the list is empty, perform no spec sync or specs-instruction
        lookup for that change; do not infer deltas from unrelated artifacts.
      - Evaluate each change independently. A missing required specs role or
        output blocks that change, even when its schema omits it.

   d. **Archive target** - Compute each change's target name once and record it as that change's `<target-name>`
      - Use the change name as-is when it already starts with a `YYYY-MM-DD-` prefix; otherwise prepend the current date as `YYYY-MM-DD-<name>` (same rule as `openspec archive`)
      - Check whether `<planningHome.changesDir>/archive/<target-name>` already exists
      - If it exists, or another selected change resolves to the same target name, mark every such change `Blocked` with `Archive directory already exists`
      - A blocked change is never synced or moved: show it as `Blocked` in the step 6 table, leave it out of conflict resolution (resolve its conflicts using only the other changes), and record it as Failed in step 8d
      - Checking here, before any main spec is written, matches `openspec archive`: a collision found after sync would leave main specs rewritten for an archive that never happened

4. **Detect spec conflicts**

   Build a map keyed by `<capability-path>`, the exact path relative to `specs/`:

   ```text
   identity/user-auth -> [change-a, change-b]  <- CONFLICT (2+ changes)
   billing/user-auth  -> [change-c]            <- OK (different full path)
   ```

   A conflict exists when 2+ selected changes have delta specs for the exact same `<capability-path>`.

5. **Resolve conflicts agentically**

   **For each conflict**, investigate the codebase:

   a. **Read the delta specs** from each conflicting change to understand what each claims to add/modify

   b. **Search the codebase** for implementation evidence:
      - Look for code implementing requirements from each delta spec
      - Check for related files, functions, or tests

   c. **Determine resolution**:
      - Missing implementation evidence blocks the entire affected change,
        including all its deltas; remove that change from the eligible batch.
      - If both are implemented, establish an evidence-backed order compatible
        with both accepted changes. Chronology alone cannot justify overwriting
        contradictory requirements; unresolved conflicts block affected changes.
      - Recompute conflicts using only eligible changes.

   d. **Record resolution** for each conflict:
      - Eligibility for each whole change and every blocking reason
      - All delta specs of eligible changes and their coherent merge order
      - Rationale (what was found in codebase)

6. **Show consolidated status table**

   Display a table summarizing all changes:

   ```markdown
   | Change              | Artifacts | Tasks | Specs   | Conflicts | Status |
   |---------------------|-----------|-------|---------|-----------|--------|
   | schema-management   | Done      | 5/5   | 2 delta | None      | Ready  |
   | project-config      | Done      | 3/3   | 1 delta | None      | Ready  |
   | add-oauth           | Done      | 4/4   | 1 delta | identity/user-auth (!) | Ready* |
   | add-verify-skill    | 1 left    | 2/5   | None    | None      | Blocked |
   ```

   For conflicts, show the resolution:
   ```text
   * Conflict resolution:
     - identity/user-auth spec: Will apply add-oauth then add-jwt (both implemented and compatible)
   ```

   For incomplete required work or unverifiable gates, show blockers:
   ```text
   Blockers:
   - add-verify-skill: 1 incomplete artifact, 3 incomplete tasks
   ```

7. **Confirm batch operation**

   Ask the user a single confirmation question:

   Offer only "Archive N ready changes" and "Cancel". If none are eligible,
   report the blockers and stop. Blocked changes cannot be confirmed into the
   batch. Show genuinely optional warnings separately.

   Route on the answer by intent, not by exact label — you wrote these labels,
   so match what the user picked rather than the wording above:
   - "Cancel" — stop, do not archive. Report that nothing was archived and skip the remaining steps.
   - The ready-changes option — proceed only with `Ready` or `Ready*` changes;
     record blocked changes as Failed with their actual reasons. Recompute
     conflict ordering if the eligible selection changes.
   - Anything else — ask again rather than archiving

   Before step 8 writes the first main spec or moves any change, fetch every
   required specs-rule snapshot for the confirmed batch. For each change that will
   sync concrete `artifactPaths.specs.existingOutputPaths`, run
   `openspec instructions specs --change "<name>" --json` exactly once with the
   same selected-root flags. Obtain all snapshots before the first write or move.
   If any lookup exits non-zero or returns invalid artifact-instruction JSON,
   identify the affected change, report the error, and stop the whole batch before
   any main-spec write or change move. Do not treat lookup failure as omitted
   rules. A valid response without `rules` is the no-rules case.

8. **Execute archive for each confirmed change**

   Before processing, retain all delta paths for each eligible change from
   `artifactPaths.specs.existingOutputPaths`. No delta may be excluded from an
   archived change. Recheck gates if artifacts or evidence changed.

   Process changes in the determined order (respecting conflict resolution):

   a. **Sync every delta of the eligible change**:
      - Run the `openspec-sync-specs` workflow inline (agent-driven intelligent
        merge) for the full delta list and wait for completion. Apply the single
        archive workflow's missing-main-spec and retirement assessment before
        writing; a sync blocker blocks the whole affected change.
      - If the sync reports any stop or blocking condition, treat the sync as failed. Stop processing that change immediately. Before continuing to the next change, record this change's outcome as Failed in the batch results, including the sync blocking/error condition.
      - Do not perform the post-sync content comparison and do not move its `changeRoot`; leave the change intact.
      - For conflicts, apply in resolved order. If a change fails, stop later
        changes sharing its capabilities or depending on it and report them as
        blocked; only independent eligible changes may continue.
      - Pass that change's fetched specs-rule snapshot into inline sync; inline
        sync must reuse it without fetching instructions again
      - Apply artifact rules only to main specs produced by that change. They do
        not change conflict resolution, archive behavior, or CLI contracts, and
        their text is not copied into an output file
      - Do not delegate to a background task — step 8c would move `changeRoot` out from under a sync that is still reading it.
      - A missing required delta list blocks the change rather than skipping sync.

   b. **Verify every delta before moving changeRoot**:
      - Re-run comparison for every delta against the main spec at
        `<planningHome.root>/openspec/specs/<capability-path>/spec.md` (use the
        store-aware root, not a hardcoded repo path). Apply the single archive
        workflow's structural checks too, including already-synced deltas.
      - Verify that main specs are updated:
        - ADDED requirements present
        - MODIFIED requirements carrying scenario and description changes named in the delta, with their other scenarios intact
        - REMOVED requirements gone — and where this sync retired a capability (removed its last requirement, leaving `## Requirements` empty), its main spec deleted rather than left empty.
        - RENAMED requirements present under the new name and absent under the old one
      - No unverified delta is permitted. Report any partial main-spec writes on
        failure without claiming rollback.
      - If sync failed or any capability does not match verification, report what differs and fail/skip moving that change's `changeRoot` — do not archive that change. `changeRoot` remains intact.

   c. **Perform the archive**:

      Target name: use the `<target-name>` recorded for this change in step 3d, unchanged. Never recompute it here: a batch that runs past midnight would check one date in step 3 and move to another.

      **Check if target already exists:**
      - Check again immediately before the move, even though step 3 already checked: the target can appear mid-batch
      - If yes: record this change as Failed with `Archive directory already exists`, leave `changeRoot` where it is, report any main specs step 8a already synced for it, and continue with the remaining changes
      - If no: move `changeRoot` to the archive directory

      ```bash
      mkdir -p "<planningHome.changesDir>/archive"
      mv "<changeRoot>" "<planningHome.changesDir>/archive/<target-name>"
      ```

      **Confirm the move did not nest:** `mv` exits 0 even when the target appeared after the check, moving the change *inside* it. If `<planningHome.changesDir>/archive/<target-name>/<change-directory-name>` now exists (the last path segment of `changeRoot`), move that directory back to `changeRoot` and record this change as Failed with `Archive directory already exists`. Never report it as archived.

   d. **Track outcome** for each change:
      - Success: archived successfully
      - Failed: error during archive or spec verification (record error)
      - Skipped: user chose not to archive (if applicable)
      - Blocked: leave the whole change active and report its reason; never
        describe an archived change as partially synced.

9. **Display summary**

   Show final results:

   ```markdown
   ## Bulk Archive Complete

   Archived 3 changes:
   - schema-management-cli -> archive/2026-01-19-schema-management-cli/
   - project-config -> archive/2026-01-19-project-config/
   - add-oauth -> archive/2026-01-19-add-oauth/

   Blocked 1 change:
   - add-verify-skill (required artifacts/tasks incomplete)

   Spec sync summary:
   - 4 delta specs synced to main specs
   - Every delta of each archived change synced and verified
   - Missing implementation blocks its whole change, not just its spec sync
   ```

   If any failures:
   ```text
   Failed 1 change:
   - some-change: Archive directory already exists
   ```

**Conflict Resolution Examples**

Example 1: Only one implemented
```text
Conflict: <planningHome.root>/openspec/specs/auth/spec.md touched by [add-oauth, add-jwt]

Checking add-oauth:
- Delta adds "OAuth Provider Integration" requirement
- Searching codebase... found src/auth/oauth.ts implementing OAuth flow

Checking add-jwt:
- Delta adds "JWT Token Handling" requirement
- Searching codebase... no JWT implementation found

Resolution: Block add-jwt entirely. Only add-oauth is eligible for sync and archive.
```

Example 2: Both implemented
```text
Conflict: <planningHome.root>/openspec/specs/api/spec.md touched by [add-rest-api, add-graphql]

Checking add-rest-api (created 2026-01-10):
- Delta adds "REST Endpoints" requirement
- Searching codebase... found src/api/rest.ts

Checking add-graphql (created 2026-01-15):
- Delta adds "GraphQL Schema" requirement
- Searching codebase... found src/api/graphql.ts

Resolution: Both implemented. Will apply add-rest-api specs first,
then add-graphql specs only if both accepted changes remain satisfied;
otherwise block the conflicting changes pending resolution.
```

**Output On Success**

```markdown
## Bulk Archive Complete

Archived N changes:
- <change-1> -> archive/<target-name-1>/
- <change-2> -> archive/<target-name-2>/

Spec sync summary:
- N delta specs synced to main specs
- No conflicts (or: M conflicts resolved)
```

**Output On Partial Success**

```markdown
## Bulk Archive Complete (partial)

Archived N changes:
- <change-1> -> archive/<target-name-1>/

Skipped M changes:
- <change-2> (not selected for archive)

Failed K changes:
- <change-3>: Archive directory already exists
```

**Output When No Changes**

```markdown
## No Changes to Archive

No active changes found. Create a new change to get started.
```

**Guardrails**
- Allow any number of changes (1+ is fine, 2+ is the typical use case)
- Always prompt for selection, never auto-select
- Detect spec conflicts early and resolve by checking codebase
- Require an evidence-backed merge order; unresolved contradictions block affected changes
- Missing implementation blocks the entire affected change, never just one delta
- Show clear per-change status before confirming
- Use single confirmation for entire batch
- Never archive after the user cancels the confirmation — a cancelled batch archives nothing
- Track and report all outcomes (success/skip/fail)
- Preserve .openspec.yaml when moving to archive
- Archive directory target uses the current date, computed once in step 3d and reused at the move: YYYY-MM-DD-<name>; a name that already starts with a `YYYY-MM-DD-` prefix is used as-is (never stack a second date)
- If archive target exists, fail that change but continue with others
- Check every archive target in step 3, before the first main-spec write; a change whose target exists is never synced or moved
- Run the `openspec-sync-specs` workflow inline (agent-driven) for every eligible change
- Sync and verify every delta before moving its changeRoot; no per-delta exclusions
- Never archive a change while a spec sync is still in flight — run the sync inline and verify main specs at `<planningHome.root>/openspec/specs/<capability-path>/spec.md` before moving `changeRoot`
- Fetch archive inputs once per selected root before spec inspection or moves
- Fetch all required specs-rule snapshots before the batch's first main-spec write or move
- A failed archive-inputs lookup never blocks the batch; it proceeds with no context or guidance
- A failed specs instruction lookup stops the whole batch atomically
- Missing required specs or task tracking blocks the entire affected change
- Apply relevant runtime context across the batch and report conflicts
- Operation guidance remains advisory; consider every entry and explain rejected advice
- Keep runtime inputs, conflict analysis, CLI-derived values, and artifact rules separate
- Artifact rules constrain only written specs
- Never copy runtime input or artifact-rule text verbatim into output files
