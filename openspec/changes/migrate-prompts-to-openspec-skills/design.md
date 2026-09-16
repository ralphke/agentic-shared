# Design: Migrate Prompt Entry Points to OpenSpec Skills

## Decision

Replace the shared prompt-file command wrappers with OpenSpec-compatible skills. The
replacement skills use the upstream `SKILL.md` format and delegate artifact discovery,
paths, and workflow state to the `openspec` CLI. Software Fabric policy remains in the
shared skills and the existing persona playbooks.

## Skill Mapping

| Current prompt | Replacement | Decision |
| --- | --- | --- |
| `opsx-propose.prompt.md` | `openspec-propose/SKILL.md` | Replace |
| `opsx-apply.prompt.md` | `openspec-apply-change/SKILL.md` | Replace |
| `opsx-verify.prompt.md` | `openspec-verify-change/SKILL.md` | Replace |
| `sdlc-kickoff.prompt.md` | `software-fabric-kickoff/SKILL.md` | Replace as an orchestrator that sequences skills and pauses after planning approval |

## Runtime Contract

Command skills require Node.js 26 or later and `@fission-ai/openspec` installed globally.
Consumer guidance must provide:

```powershell
npm install -g @fission-ai/openspec@latest
openspec init
openspec context --json
```

`openspec init` must preserve the consumer's `openspec/` path configuration. Before
the command skills modify artifacts, they must verify that `openspec` is available and
that `openspec context --json` resolves an OpenSpec root. On failure they report the
prerequisite and stop; legacy prompt behavior is not a fallback.

## Workflow Behavior

1. A GitHub issue labelled `idea` is the primary non-developer intake. The Product Owner
   Agent reads its title, form fields, labels, and discussion when creating a proposal;
   the issue remains `idea` and `stage:proposal` until planning approval.
2. Direct `/opsx:propose` remains a valid route for users who want to create a proposal
   without opening an issue.
3. The proposal skill creates every artifact transitively required by the selected schema
   and stops at the planning boundary.
4. The apply skill obtains status, context files, and instructions from the CLI, reads all
   returned context, and completes only unchecked tasks.
5. The verification skill evaluates task completeness, requirement/scenario coverage, and
   design coherence, then invokes the existing Software Fabric test, security, legal, and
   review requirements before archiving.
6. The kickoff skill invokes proposal behavior, presents planning artifacts for approval,
   then invokes apply and verification only after a new explicit user request.

## Consumer Migration

The release keeps the `prompts` asset group for one compatibility release. It documents
the replacement command names and deprecation schedule. Consumers with `prompts: local`
or `.github/prompts/local/**` retain their local assets. A later, separately proposed
breaking release removes shared prompts after telemetry or consumer confirmation shows
the replacement skills have been adopted.

## Validation

- Add structural tests for skill front matter, prerequisite guardrails, command mapping,
  and planning-only behavior.
- Extend sync tests to prove replacement skills copy correctly and local prompt extensions
  remain untouched.
- Run the repository Python test suite and manifest validation.

## ADRs

### ADR-001: Use the OpenSpec CLI as the workflow source of truth

Upstream maintains schema-specific artifact order, resolved locations, and workflow
instructions. Skills must query the CLI instead of duplicating those assumptions.

### ADR-002: Require Node.js 26+ in adopters of command skills

The migration standardizes the consumer runtime on Node.js 26 or later. This requirement
applies to consumers that use command skills, not to repositories that only consume the
shared static artifacts.

### ADR-003: Transition prompts instead of deleting them in the first skills release

Consumer configurations and local prompt extensions must not be silently broken. The
first release publishes replacements and migration guidance; prompt removal is deferred to
a separately reviewed breaking change.