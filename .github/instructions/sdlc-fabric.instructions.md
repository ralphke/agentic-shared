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
       → [Tests] → [Security] → [Review] → [Deploy] → [Operate]
```

Each stage is owned by a specific persona defined in `.github/agents/`.
Stages are gated by GitHub PR labels (`stage:*`).

## Agent Personas

| Persona              | File                                  | Stage Label      |
|----------------------|---------------------------------------|------------------|
| Product Owner        | `.github/agents/product-owner.md`     | `stage:design`   |
| Systems Architect    | `.github/agents/architect.md`         | `stage:implement`|
| Developer            | `.github/agents/developer.md`         | `stage:test`     |
| QA Engineer          | `.github/agents/qa-engineer.md`       | `stage:security` |
| Security Engineer    | `.github/agents/security-engineer.md` | `stage:review`   |
| Code Reviewer        | `.github/agents/code-reviewer.md`     | `stage:deploy`   |
| DevOps/SRE           | `.github/agents/devops-sre.md`        | `stage:operate`  |
| Operations SRE       | `.github/agents/operations-sre.md`    | `archived`       |

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
3. **No deploy without tests** — coverage ≥ 80%
4. **No archive without SLOs** — operations must be configured
5. **Document decisions** — use ADRs for architectural choices

## MCP Servers Available

See `.vscode/mcp.json` for configured MCP servers:
- `openspec-filesystem` — read/write specs in `spec/openspec/`
- `github-mcp` — GitHub API for issues, PRs, and workflow triggers
