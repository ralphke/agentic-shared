---
applyTo: "**"
---

# Software Fabric — Autonomous SDLC Instructions

This repository uses the **Software Fabric** pattern: a spec-driven autonomous
SDLC where AI agent personas collaborate through a structured pipeline from idea
to production.

## Work Mode

Existing Fabric consumers use Fabric mode by default. For the current work,
a user may explicitly select standalone OpenSpec, in which case Fabric agent
orchestration is not an OpenSpec requirement. This selection does not bypass
repository-level merge or release controls. In Fabric mode, use
`fabric-propose` for new planning and preserve all applicable Fabric gates.
The Software Fabric personas and all stage, intake, and planning rules in this
integration govern Fabric mode only.
For an explicit standalone selection, use the corresponding upstream skill
unchanged and do not perform these Fabric agent steps. The advisory selector
is `python .github/skills/fabric-propose/scripts/route_fabric_workflow.py --action <action>`; append
`--mode standalone` only for an explicit selection. Do not infer that mode from
an upstream skill name. Mode and selected store remain sticky across handoffs.
GitHub stage labels describe orchestration; they do not enforce gate clearance.

## How the Software Fabric Works

```text
[Idea] → [Proposal] → [UX Design*] → [Spec+Design] → [Tasks] → [Code]
       → [Tests] → [Security] → [Legal Review*] → [Review] → [Deploy] → [Operate]
```

`UX Design*` applies only when the accepted change affects a visual interface.
Record `## UX Applicability` in the proposal with boolean `required` and a
scope-backed `reason`. CLI-only, API-only, and framework changes with no affected
visual interface require no UX stage, brief, UX-specific specs, or UX tests;
route directly to `stage:design` and retain normal functional quality gates.
Mixed changes require UX only for affected visual surfaces. Missing or
conflicting applicability blocks handoff rather than implying an exemption.

`Legal Review*` is an optional escalation gate triggered only when the proposal
or implementation is assessed as high-risk for legal, regulatory, licensing, or
use-rights issues. The persona currently owning the active stage (Product Owner,
UX Designer, Architect, or Developer) must perform this risk assessment at the
end of their stage and label the PR `stage:legal` if any trigger criteria are met.

Each stage is owned by a specific persona defined in `.github/agents/`. Stages
are gated by GitHub PR labels (`stage:*`). If a PR has no stage label, apply
`stage:proposal` by default. If multiple stage labels are present, treat the
earliest stage in the pipeline as authoritative and flag the conflict for human
review.

## Agent Personas

| Persona            | File                                        | Stage Label       |
| ------------------ | ------------------------------------------- | ----------------- |
| Product Owner      | `.github/agents/product-owner.agent.md`     | `stage:proposal`  |
| UX Designer        | `.github/agents/ux-designer.agent.md`       | `stage:ux`        |
| Systems Architect  | `.github/agents/architect.agent.md`         | `stage:design`    |
| Developer          | `.github/agents/developer.agent.md`         | `stage:implement` |
| QA Engineer        | `.github/agents/qa-engineer.agent.md`       | `stage:test`      |
| Security Engineer  | `.github/agents/security-engineer.agent.md` | `stage:security`  |
| Legal & Compliance | `.github/agents/legal-compliance.agent.md`  | `stage:legal`     |
| Code Reviewer      | `.github/agents/code-reviewer.agent.md`     | `stage:review`    |
| DevOps/SRE         | `.github/agents/devops-sre.agent.md`        | `stage:deploy`    |
| Operations SRE     | `.github/agents/operations-sre.agent.md`    | `stage:operate`   |

## To Start a New Feature

1. Create a GitHub Issue using the "💡 Idea Capture" template, OR
2. Run `/fabric-propose <idea-slug>` in VS Code Copilot chat

## To Work on an Existing Change

```text
/fabric-apply-change <change-slug>    # Implement tasks
/fabric-sync-specs <change-slug>     # Preview spec merge
/fabric-archive-change <change-slug>  # Complete the change
```

## Spec Location Convention

All specs live in `openspec/`:

- `openspec/specs/` — source of truth (domain specs)
- `openspec/changes/` — in-flight change proposals
- `openspec/config.yaml` — OpenSpec project config

## Key Rules for All Personas

Before capturing a new idea, follow the **Pre-Capture Intake Decision** in
`.github/instructions/fabric-workflow.instructions.md`: assess outside the
worktree and offer Proceed, Defer, or Do not pursue. Missing input pauses capture.
Defer or rejection ends intake without repository writes or successful archive;
it never authorizes deleting existing work. Explicit Proceed is capture
authorization only, not proposal/spec acceptance or implementation approval.

1. **No code before accepted planning** — complete proposal, delta specs, design,
   and tasks are required; verify explicit acceptance of the current
   proposal/spec before implementation. CLI readiness or skipped required
   artifacts cannot waive this gate.
2. **No merge without security** — security gate must pass
3. **No release without legal review when the proposal is high-risk** — if a
   solution risks fines, legal violations, unauthorized handling of PII or
   sensitive data, rights conflicts, or non-compliant third-party use, the Legal
   & Compliance Agent must be included before review or deployment can proceed.
4. **No deploy without tests** — coverage ≥ 80%
5. **No archive without SLOs** — operations must be configured
6. **Document decisions** — use ADRs for architectural choices
7. **No archive overrides** — required artifacts/tasks and every mandatory quality
   gate must be complete and verifiable before archive-driven sync or moves.
   Confirmation cannot override them. Sync and verify every delta before archive,
   including bulk archive; an unsatisfied delta blocks its whole change.
   Follow `.github/instructions/fabric-workflow.instructions.md` for the
   complete planning and archive checklist; optional-artifact warnings remain
   informative rather than mandatory.

## High-Risk Trigger for Legal Review

A change must trigger the Legal & Compliance Agent immediately when it is
assessed as high-risk for any of the following:

- potential regulatory breach or violation of applicable laws
- exposure or tampering with PII, personal data, health data, financial data, or
  other sensitive information
- risk of civil or criminal penalties, fines, sanctions, or enforcement actions
- third-party component use that may create licensing, rights, or contract
  conflicts
- use of AI, data, or content sources with unclear ownership or usage rights
- integration with external services, datasets, or regions that may impose legal
  or policy gaps
- two or more of the above specific factors apply simultaneously

> Strong rule: if the proposal is identified as high-risk, legal review is not
> optional. The solution must not advance to review, deploy, or operate stages
> until the Legal & Compliance Agent has assessed the exposure and either
> cleared the change or mandated remediation, escalation, or a formal legal
> sign-off. If remediation is mandated, the PR must remain labeled `stage:legal`
> until the Legal & Compliance Agent re-reviews and clears the change.

## MCP Servers Available

See `.vscode/mcp.json` for configured MCP servers:

- `openspec-filesystem` — read/write specs in `openspec/`
- `github-mcp` — GitHub API for issues, PRs, and workflow triggers
