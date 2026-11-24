# Design

## Context

The audit established three categories of defects:

1. Invalid or stale active deltas that no longer reconcile with canonical specs.
2. Canonical contracts that omit required persona, applicability, or archive
   evidence.
3. Strict-format issues caused by duplicated structure, long requirement
   descriptions, non-normative role text, and inconsistent delta headers.

The canonical specs, active changes, workflow instructions, and persona
definitions must be repaired together. Existing uncommitted edits in
`idea-capture`, `operations`, and `personas` are user work and must be
integrated rather than reset. See `proposal.md` for motivation and scope.

## Goals / Non-Goals

**Goals:**

- Produce an archive-safe reconciliation for every critical active delta.
- Make each handoff identify accountable owner, required inputs, outputs,
  evidence, blockers, and next role.
- Permit legitimate role overlap through recorded collaboration and a
  common-ground dispute procedure.
- Make canonical requirements and workflow instructions mutually consistent.
- Achieve zero errors and zero warnings from strict OpenSpec validation.
- Preserve useful scenarios unless a retained or retired decision is explicitly
  recorded.

**Non-Goals:**

- Redesigning the Software Fabric stage order.
- Treating the Product Owner's capture request as proposal acceptance.
- Archiving unrelated active changes or asserting external quality gates.
- Creating UX artifacts for this nonvisual governance change.
- Replacing maintainer decisions about legal, security, or operational risk.

## Decisions

### Decision 1: Reconcile active deltas by intent, not mechanically

For each invalid or stale delta:

1. Compare the delta requirement with the exact current canonical requirement.
2. Inventory every current and delta scenario by normalized name.
3. Classify each omitted scenario as:
   - retain unchanged,
   - retain with updated wording,
   - retire with reason and migration/replacement, or
   - duplicate and consolidate.
4. Convert stale `ADDED` requirements that already exist canonically into
   complete `MODIFIED` requirements when the historical change still owns that
   behavior.
5. Re-run validation and the archive-conflict preview.

This preserves historical intent and avoids assuming that omission always means
either retention or removal.

**Alternative considered:** Copy every missing scenario mechanically.

Rejected because some historical scenarios may genuinely be obsolete. The
accepted rule is explicit evaluation and evidence, not blind restoration.

### Decision 2: Use primary ownership with permitted collaboration

Every persona and handoff contract identifies one primary accountable owner.
Other personas may contribute, challenge, or provide evidence, but the contract
records them as collaborators. If overlap is disputed, the current stage owner
documents the competing interpretations and escalates to the Architect or a
responsible human maintainer for a common-ground decision.

This prevents overlap from becoming either an exclusivity fiction or an
ownership vacuum.

**Alternative considered:** Require exclusive ownership for every artifact.

Rejected because several activities legitimately need Product Owner, UX, QA,
Architect, or operational contributions.

### Decision 3: Normalize formatting without changing semantics

Formatting fixes are separate from behavioral reconciliation:

- one `## Purpose` section per canonical spec;
- `# Delta for <domain>` on active deltas;
- current repository heading and scenario marker format;
- normative `MUST` or `SHALL` text for gating requirements;
- descriptions of 500 characters or fewer by splitting unrelated behaviors
  into separate requirements only when their scenarios remain traceable.

Semantic changes require an explicit delta requirement or documented scenario
decision; formatting cleanup must not silently remove a rule.

**Alternative considered:** Fix only validation errors.

Rejected because strict warnings and structural duplication would continue to
make the source inconsistent and acceptance evidence ambiguous.

### Decision 4: Treat strict CLI validation as necessary, not sufficient

`openspec validate --all --strict --json` is the structural exit command.
Implementation must also run a focused contract audit covering:

- all active delta headers and sections;
- complete requirement and scenario preservation;
- duplicate requirement names across canonical and `ADDED` deltas;
- persona contract fields;
- stage entry, exit, next-owner, evidence, and blocker clauses;
- mandatory gate parity with
  `.github/instructions/openspec-workflow.instructions.md`.

CLI validity does not prove that external quality gates passed.

**Alternative considered:** Rely only on OpenSpec validation.

Rejected because CLI validation does not detect ambiguous role ownership or
incomplete handoff semantics.

### Decision 5: Repair existing active changes in place

The affected active change folders are retained and repaired:

- `migrate-prompts-to-openspec-skills`
- `add-ux-designer-persona`
- `conditional-ux-stage-and-validation`
- `strengthen-ux-designer-brief-workflow`

Stale `ADDED` blocks are converted to complete `MODIFIED` blocks that reflect the
existing canonical requirement and the change's intended contribution. The
invalid `migrate-prompts-to-openspec-skills` blocks are rebuilt from the full
canonical requirements. Active changes are not archived or deleted by this
change.

**Alternative considered:** Delete completed active changes after copying their
content to canonical specs.

Rejected because it loses the planning history and bypasses archive evidence.

### Decision 6: Preserve and integrate uncommitted source-spec edits

Before any file-level edit, inspect the current diff and preserve valid content.
Implementation integrates the Purpose edits in `idea-capture`, `operations`, and
`personas`; it corrects duplicate separators or headings in place rather than
resetting the files.

**Alternative considered:** Revert the uncommitted edits to repository HEAD.

Rejected because those edits belong to the current worktree and contain useful
structural cleanup.

### Decision 7: Scope devcontainer security overrides to validation warnings

The devcontainer validation lane may record an approved HIGH or CRITICAL image
finding as `security:devcontainer-warning` only when a security reviewer records:

- the exact finding and affected image component;
- why the finding is limited to local devcontainer validation;
- the named remediation owner;
- the expiry or renewal point;
- a linked mandatory follow-up issue or task; and
- current evidence that no production or release gate is being evaluated.

The warning is an explicit exception outcome, never a passed or accepted-risk
result for application code, merge, release, deployment, or archive. Expired or
incomplete exceptions revert to blocking behavior.

**Alternative considered:** Disable HIGH/CRITICAL security checks for the
devcontainer image.

Rejected because it would erase the finding, provide no renewal pressure, and
could be misread as security clearance.

## Risks / Trade-offs

- [Historical scenario still matters but appears obsolete] -> Review the
  scenario against its current source requirement and record why it is retained,
  updated, or retired; do not infer from age alone.
- [Converting stale `ADDED` blocks to `MODIFIED` obscures the original change]
  -> Retain the change folder and proposal history, and make the MODIFIED block
  include the change's original scenarios.
- [Strict cleanup changes wording during semantic repair] -> Keep semantic and
  formatting edits in separate tasks and compare requirement names and scenario
  inventories after each phase.
- [A complete persona matrix creates duplication] -> Keep canonical persona
  requirements as the contract and use `.github/agents/*.agent.md` as the
  executable persona implementation, then test for parity.
- [A devcontainer warning is mistaken for security approval] -> Use a distinct
  label and output state, carry it nowhere outside the devcontainer lane, and
  keep mandatory follow-up, owner, and expiry evidence attached.
- [Current external gate evidence is unavailable] -> Report the gate as
  unverified; never mark archive readiness from local validation alone.

## Migration Plan

1. Snapshot the active-change scenario inventory and current source requirement
   names.
2. Repair the two invalid `MODIFIED` blocks and all stale `ADDED` blocks.
3. Normalize delta headers and canonical heading/layout defects.
4. Update canonical `idea-capture`, `personas`, and `sdlc-process` contracts to
   match the accepted deltas.
5. Align persona agent definitions and workflow instructions with the canonical
   contracts where current text contradicts them, including the scoped
   devcontainer warning lane.
6. Split overlong descriptions and add missing normative language without
   dropping scenarios.
7. Run strict OpenSpec validation and focused contract audits.
8. Sync only this approved change's deltas into canonical specs after the
   validation and review evidence required by policy is available.

Rollback is a Git review/revert of the specific specification edits. No
deployment rollback, data migration, or external resource mutation is involved.

## Open Questions

None. The accepted proposal and delta specs resolve the scope, ownership,
scenario-review, and nonvisual-applicability decisions.
