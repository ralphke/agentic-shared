# Copilot instructions

## Repository snapshot

This repository contains a GitHub Copilot workshop scaffold with beginner, intermediate, and advanced learning paths.

Primary workshop artifacts:

- README.md
- doc/setup.md
- doc/environments.md
- doc/workshop-roadmap.md
- lab/beginner/01-copilot-foundations.md
- lab/intermediate/01-tests-and-refactor.md
- lab/intermediate/02-spec-driven-development.md
- lab/advanced/01-agentic-cicd.md
- lab/advanced/02-agentic-lifecycle.md
- spec/spec-template.md
- spec/example-feature-spec.md
- .devcontainer/devcontainer.json
- .devcontainer/post-create.sh
- .github/ISSUE_TEMPLATE/copilot-task.yml
- .github/workflows/ci.yml
- .github/workflows/copilot-task-router.yml

## Commands

The devcontainer provides the following tools:

```bash
python3 --version                              # Python 3.14.x
python3 -m pytest                              # Run Python tests
dotnet --version                               # .NET 10.x
dotnet run                                     # Run .NET project in cwd
dotnet test                                    # Run .NET tests
dab --version                                  # Data API Builder
dab init -c dab-config.json --database-type mssql --connection-string "<cs>"
dab add <entity> --source <table> --permissions "anonymous:*"
dab start                                      # Start the DAB API server
docker version                                 # Host Docker (via socket)
```

Current validation runs through GitHub Actions:

- CI workflow validates workshop file structure (including devcontainer files).
- CI workflow validates devcontainer.json is parseable JSON and post-create.sh has a shebang.
- CI workflow validates ordered prompt naming in .github/prompts.

## Architecture

The repository is organized as a workshop content and automation blueprint:

- doc/: facilitator and roadmap documentation; doc/setup.md is the participant prerequisite guide; doc/environments.md documents the devcontainer and device matrix.
- lab/: participant exercises by skill level. All labs assume VS Code Agents application as primary IDE.
- spec/: reusable spec templates and examples for spec-driven development exercises.
- .devcontainer/: devcontainer configuration — Python 3.14, .NET 10, Aspire, DAB, docker-outside-of-docker.
- .github/prompts/: chronological prompt history.
- .github/workflows/: CI and issue-to-Copilot routing automation.

## IDE

The primary IDE for all workshop participants is the **VS Code Agents application** (bundled with VS Code Insiders). Reference doc/setup.md for installation steps. All lab exercises are written for the agent-first workflow in the Agents app.

## Target runtimes

- Python 3.14 (installed via devcontainer feature)
- .NET 10 SDK (installed via devcontainer feature)
- .NET Aspire workload (installed in post-create.sh)
- Data API Builder / DAB (installed in post-create.sh as `dotnet tool install -g microsoft.dataapibuilder`)
- Docker CLI via docker-outside-of-docker (host socket mounted)

## Conventions

- Use the repo tree and any newly added config files as the source of truth.
- Record every workshop-building prompt in .github/prompts in operation order using zero-padded numeric prefixes.
- Keep issue-to-Copilot automation centered on the copilot-task label and Copilot Task issue template.
- If project tooling is added later, update this file with exact commands and repo-specific patterns.

---

## Software Fabric — Autonomous SDLC

This repository implements a **spec-driven autonomous SDLC** using the [OpenSPEC](https://github.com/Fission-AI/OpenSpec) specification format. The goal: submit an idea, and the Software Fabric pipeline autonomously produces a tested, secure, deployable application.

### Pipeline at a Glance

```
[Idea Issue] → [Proposal] → [Design+Tasks] → [Code] → [Tests]
             → [Security] → [Review] → [Deploy] → [Operate+Archive]
```

Stages are tracked via PR labels: `stage:proposal` → `stage:design` → `stage:implement` → `stage:test` → `stage:security` → `stage:review` → `stage:deploy` → `stage:operate` → `archived`

### Entry Points

| Method | Command/Path |
|--------|-------------|
| Submit an idea | Open an issue using `.github/ISSUE_TEMPLATE/idea-capture.yml` |
| Start pipeline in chat | Use `.github/prompts/sdlc-kickoff.prompt.md` |
| Propose a change | `/opsx:propose <slug>` (prompt: `opsx-propose.prompt.md`) |
| Implement a change | `/opsx:apply <slug>` (prompt: `opsx-apply.prompt.md`) |
| Verify a change | `/opsx:verify <slug>` (prompt: `opsx-verify.prompt.md`) |

### OpenSPEC Structure (`spec/openspec/`)

- `config.yaml` — project config, domain ownership, quality gates, persona roster
- `specs/<domain>/spec.md` — source-of-truth requirement specs (MUST/SHALL + Given/When/Then)
- `changes/<slug>/` — in-flight work: `proposal.md`, `design.md`, `tasks.md`, `specs/<domain>/spec.md` (delta)
- `changes/archive/` — completed, archived changes

**Domains:** `sdlc-process`, `personas`, `idea-capture`, `security-standards`, `testing-standards`, `operations`

**Delta spec format inside a change:**
```markdown
## ADDED Requirements
## MODIFIED Requirements
## REMOVED Requirements
```

### Agent Personas (`.github/agents/`)

| File | Role | Trigger |
|------|------|---------|
| `product-owner.md` | Idea → `proposal.md` | `idea` label |
| `architect.md` | Proposal → `design.md` + `tasks.md` | `stage:design` |
| `developer.md` | Tasks → implementation | `stage:implement` |
| `qa-engineer.md` | Code → test suites (≥80% coverage) | `stage:test` |
| `security-engineer.md` | Code → security report (OWASP) | `stage:security` |
| `code-reviewer.md` | Code → review (BLOCKING/SUGGESTION) | `stage:review` |
| `devops-sre.md` | Merge → staged deploy + rollback | `stage:deploy` |
| `operations-sre.md` | Deploy → SLOs + dashboards + archive | `stage:operate` |

### Skills (`.github/skills/`)

| File | Used By | Purpose |
|------|---------|---------|
| `idea-to-spec.md` | Product Owner | Transform raw idea to proposal.md |
| `spec-to-design.md` | Architect | Proposal → design.md + tasks.md |
| `test-generation.md` | QA Engineer | Spec scenarios → test suites |
| `security-review.md` | Security Engineer | SAST + OWASP audit |
| `pr-review.md` | Code Reviewer | Quality + design alignment review |
| `deploy-pipeline.md` | DevOps SRE | Staged deploy with smoke tests |

### Quality Gates

All must pass before a change can be archived:
- ✅ CI green (tests passing)
- ✅ Test coverage ≥ 80%
- ✅ No CRITICAL or HIGH security findings
- ✅ ≥ 1 code review approval
- ✅ All `tasks.md` items checked
- ✅ All `proposal.md` acceptance criteria checked

### MCP Servers (`.vscode/mcp.json`)

| Server | Purpose |
|--------|---------|
| `openspec-filesystem` | Read/write `spec/openspec/` folder |
| `github-mcp` | Create/label issues and PRs |

**OpenSpec CLI install:** `npm install -g @fission-ai/openspec@latest`

### Instruction Files

- `.github/instructions/openspec-workflow.instructions.md` — applied to `spec/openspec/**`
- `.github/instructions/sdlc-fabric.instructions.md` — applied globally (`**`)
