---
applyTo: "**"
---

# Software Fabric — Autonomous SDLC Instructions

This repository uses the **Software Fabric** pattern: a spec-driven autonomous
SDLC where AI agent personas collaborate through a structured pipeline from
idea to production.

## How the Software Fabric Works

```
[Idea] → [Proposal] → [Spec+Design] → [Tasks] → [Code]
       → [Tests] → [Security] → [Legal Review*] → [Review] → [Deploy] → [Operate]
```

`Legal Review*` is an optional escalation gate triggered only when the proposal or
implementation is assessed as high-risk for legal, regulatory, licensing, or use-rights issues.
The persona currently owning the active stage (Product Owner, Architect, or Developer) must perform this risk assessment at the end of their stage and label the PR `stage:legal` if any trigger criteria are met.

Each stage is owned by a specific persona defined in `.github/agents/`.
Stages are gated by GitHub PR labels (`stage:*`).
If a PR has no stage label, apply `stage:proposal` by default. If multiple stage labels are present, treat the earliest stage in the pipeline as authoritative and flag the conflict for human review.

## Agent Personas

| Persona              | File                                  | Stage Label      |
|----------------------|---------------------------------------|------------------|
| Product Owner        | `.github/agents/product-owner.agent.md` | `stage:proposal` |
| Systems Architect    | `.github/agents/architect.agent.md`           | `stage:design`   |
| Developer            | `.github/agents/developer.agent.md`           | `stage:implement`|
| QA Engineer          | `.github/agents/qa-engineer.agent.md`         | `stage:test`     |
| Security Engineer    | `.github/agents/security-engineer.agent.md`  | `stage:security` |
| Legal & Compliance   | `.github/agents/legal-compliance.agent.md`   | `stage:legal`    |
| Code Reviewer        | `.github/agents/code-reviewer.agent.md`      | `stage:review`   |
| DevOps/SRE           | `.github/agents/devops-sre.agent.md`         | `stage:deploy`   |
| Operations SRE       | `.github/agents/operations-sre.agent.md`    | `stage:operate`  |

## To Start a New Feature

1. Create a GitHub Issue using the "💡 Idea Capture" template, OR
2. Run `/opsx:propose <idea-slug>` in VS Code Copilot chat

## To Work on an Existing Change

```
/opsx:apply <change-slug>    # Implement tasks
/opsx:sync <change-slug>     # Preview spec merge
/opsx:archive <change-slug>  # Complete the change
```

## Spec Location Convention

All specs live in `spec/openspec/`:
- `spec/openspec/specs/` — source of truth (domain specs)
- `spec/openspec/changes/` — in-flight change proposals
- `spec/openspec/config.yaml` — OpenSpec project config

## Key Rules for All Personas

1. **No code before spec** — `tasks.md` must exist before implementation
2. **No merge without security** — security gate must pass
3. **No release without legal review when the proposal is high-risk** — if a solution risks
   fines, legal violations, unauthorized handling of PII or sensitive data, rights conflicts,
   or non-compliant third-party use, the Legal & Compliance Agent must be included before
   review or deployment can proceed.
4. **No deploy without tests** — coverage ≥ 80%
5. **No archive without SLOs** — operations must be configured
6. **Document decisions** — use ADRs for architectural choices

## High-Risk Trigger for Legal Review

A change must trigger the Legal & Compliance Agent immediately when it is assessed as high-risk
for any of the following:

- potential regulatory breach or violation of applicable laws
- exposure or tampering with PII, personal data, health data, financial data, or other
  sensitive information
- risk of civil or criminal penalties, fines, sanctions, or enforcement actions
- third-party component use that may create licensing, rights, or contract conflicts
- use of AI, data, or content sources with unclear ownership or usage rights
- integration with external services, datasets, or regions that may impose legal or policy gaps
- two or more of the above specific factors apply simultaneously

> Strong rule: if the proposal is identified as high-risk, legal review is not optional. The
> solution must not advance to review, deploy, or operate stages until the Legal & Compliance
> Agent has assessed the exposure and either cleared the change or mandated remediation,
> escalation, or a formal legal sign-off.
> If remediation is mandated, the PR must remain labeled `stage:legal` until the Legal & Compliance Agent re-reviews and clears the change.

## MCP Servers Available

See `.vscode/mcp.json` for configured MCP servers:
- `openspec-filesystem` — read/write specs in `spec/openspec/`
- `github-mcp` — GitHub API for issues, PRs, and workflow triggers
