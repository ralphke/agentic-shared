# Tasks

## 1. Establish the reconciliation baseline

- [x] 1.1 Inventory canonical requirement names and scenarios plus each
  affected active delta by normalized name; verify the inventory includes every
  scenario reported missing and every stale `ADDED` requirement.
- [x] 1.2 Classify every inventoried active-delta omission as retained,
  updated, retired with reason and migration, or duplicate; verify the
  classification is recorded in the edited delta or task evidence.
- [x] 1.3 Re-read the existing diffs for
  `openspec/specs/idea-capture/spec.md`,
  `openspec/specs/operations/spec.md`, and
  `openspec/specs/personas/spec.md`; verify the implementation preserves or
  intentionally supersedes each current edit.

## 2. Repair active delta changes

- [x] 2.1 Repair `migrate-prompts-to-openspec-skills/specs/personas/spec.md`
  from the complete canonical Product Owner and Developer requirement blocks;
  verify every retained scenario is present and the change validates strictly.
- [x] 2.2 Repair `migrate-prompts-to-openspec-skills/specs/sdlc-process/spec.md`
  from the complete canonical Idea-First Development and Ordered Agent
  Handoffs blocks; verify each omitted scenario has a documented disposition.
- [x] 2.3 Convert stale `ADDED` persona requirements in
  `add-ux-designer-persona` to complete, archive-safe blocks; verify retained
  UX Designer and Architect scenarios match the source inventory.
- [x] 2.4 Reconcile stale `ADDED` blocks in
  `conditional-ux-stage-and-validation` with complete canonical persona
  behavior; verify the delta no longer attempts to add existing requirements.
- [x] 2.5 Reconcile stale `ADDED` blocks in
  `strengthen-ux-designer-brief-workflow` with complete canonical persona
  behavior; verify the delta contains no duplicate additions.
- [x] 2.6 Normalize nonconforming active delta titles in the Operations SRE
  mapping and Fabric trace changes; verify each is headed
  `# Delta for <domain>` and still validates strictly.

## 3. Complete canonical source contracts

- [x] 3.1 Update `openspec/specs/idea-capture/spec.md` with required UX
  applicability, current proposal acceptance, and stale-acceptance behavior;
  verify duplicate Purpose structure is removed and all scenarios remain.
- [x] 3.2 Update the Product Owner requirement in
  `openspec/specs/personas/spec.md` with responsibilities, inputs, outputs,
  trigger, completion evidence, blockers, handoff, and agent file; verify its
  scenarios still cover measurable criteria and applicability ambiguity.
- [x] 3.3 Update the UX Designer requirement with the same complete contract
  fields; verify visual, nonvisual, mixed-scope, blocker, and technology-risk
  scenarios remain represented.
- [x] 3.4 Add the accountable-collaboration and common-ground dispute protocol to
  the persona collaboration contract; verify legitimate overlap is not forced
  into an exclusive-owner failure.
- [x] 3.5 Add explicit `MUST` or `SHALL` obligations to Security Engineer, Code
  Reviewer, DevOps/SRE, and Operations/SRE requirements; verify the original
  responsibilities and scenarios are unchanged in meaning.
- [x] 3.6 Update `openspec/specs/sdlc-process/spec.md` so handoffs define current
  owner, next role, acceptance evidence, and blockers, including overlap
  escalation; verify the stage order remains unchanged.
- [x] 3.7 Expand the canonical archive and quality-gate contracts to include
  current acceptance, all tasks, scenario tests, removed references, strict
  validation, CI, coverage, security, code review, legal, delta synchronization,
  and applicable operations evidence; verify every omitted mandatory item from
  `.github/instructions/openspec-workflow.instructions.md` is represented.
- [x] 3.8 Remove the duplicate Purpose block in
  `openspec/specs/operations/spec.md`; verify no operational requirement or
  scenario changes.
- [x] 3.9 Update `openspec/specs/security-standards/spec.md` with the scoped
  devcontainer warning exception; verify it records finding, justification,
  reviewer, owner, expiry, and mandatory follow-up without becoming a pass.

## 4. Resolve strict-format findings without semantic loss

- [x] 4.1 Split or simplify each overlong requirement description in
  `idea-capture`, `operations`, `personas`, `sdlc-process`,
  `security-standards`, and `testing-standards`; verify extracted behavior is
  preserved in complete requirements and scenarios rather than deleted.
- [x] 4.2 Normalize active and canonical scenario markers to the repository
  format while preserving GIVEN, WHEN, THEN, and AND conditions; verify strict
  validation raises no scenario-trigger or scenario-outcome warnings.
- [x] 4.3 Run a requirement/scenario diff against the pre-edit inventory; verify
  no unnamed requirement or scenario was lost and each intentional retirement
  has reason and migration evidence.

## 5. Align executable persona and workflow guidance

- [x] 5.1 Update `.github/agents/product-owner.agent.md` and
  `.github/agents/ux-designer.agent.md` only where needed to match the complete
  canonical contracts; verify each agent has unambiguous input, output,
  blocker, evidence, and handoff text.
- [x] 5.2 Audit `.github/agents/architect.agent.md` and the remaining persona
  files against the canonical ownership, normative-language, and collaboration
  rules; verify any required alignment edit preserves existing stage
  responsibilities.
- [x] 5.3 Audit `.github/instructions/openspec-workflow.instructions.md` and
  shared OpenSpec skills for contradictions with the repaired contracts;
  verify they agree on acceptance, UX applicability, delta reconciliation,
  mandatory gates, handoff blockers, and the non-transferable devcontainer
  warning.
- [x] 5.4 Update directly related documentation only where it still describes
  stale persona ownership or handoff behavior; verify no retired contradiction
  remains in a referenced canonical document.

## 6. Verify the integrated result

- [x] 6.1 Run `openspec validate --all --strict --json` and verify zero failed
  items, errors, and warnings.
- [x] 6.2 Run focused searches and structural checks to verify every active delta
  starts with `# Delta for <domain>`, every requirement has a normative rule and
  scenario, and no `ADDED` requirement duplicates a canonical heading.
- [x] 6.3 Verify each stage contract records one accountable owner, permitted
  collaborators, required evidence, explicit blockers, and next responsible
  role without incorrectly rejecting legitimate overlap.
- [x] 6.4 Verify the devcontainer warning cannot satisfy application, merge,
  release, deployment, or archive security gates and expires to blocking
  behavior when owner, expiry, or follow-up evidence is absent.
- [x] 6.5 Re-run the repository-wide audit for scenario preservation, archive
  gate parity, and persona/handoff completeness; verify all five original
  critical findings have objective evidence of closure.
- [x] 6.6 Review the final diff against unrelated worktree changes and verify no
  user edit was reverted or unrelated file was modified.

## Workflow follow-up

- Obtain current acceptance of the proposal, deltas, and design before apply.
- Sync this change's verified deltas into the canonical specs only after the
  applicable policy gates have current evidence.
- Archive this change and repaired active changes separately when each change
  independently satisfies all mandatory archive gates.
- Never report external test, security, legal, review, CI, coverage, or
  operational evidence as passed without source evidence.
