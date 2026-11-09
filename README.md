# Agentic-shared

Shared reusable agentic SDLC assets for Ralph's repositories.

## Purpose

This repository is the **single source of truth** for the reusable agentic
artifacts that were previously split across project repositories. It is also a
standalone OpenSpec root.

OpenSpec is the underlying change-management mechanism for the shared command
skills: it resolves specifications, in-flight changes, planning artifacts,
validation, and archival through the OpenSpec CLI. A clone of this repository
can be registered as a machine-local OpenSpec store when shared specifications
need to be operated on explicitly.

It currently centralizes:

- GitHub issue templates
- Agent persona definitions
- Skill playbooks
- Copilot instructions and command skills
- Event-driven GitHub workflow definitions
- Agent-ready spec templates
- Workflow retrospective automation for continuous process improvement

## Repository layout

- `.github/workflows/` - canonical workflow definitions intended to be
  synchronized into consumer repos
- `.github/ISSUE_TEMPLATE/` - shared issue intake forms
- `.github/agents/` - persona definitions used by the Software Fabric flow
- `.github/skills/` - reusable task playbooks for those personas
- `.github/instructions/` - shared instruction files
- `.github/copilot-instructions.md` - shared baseline Copilot guidance
- `.github/scripts/` - manifest validation and consumer synchronization tools
- `openspec/` - standalone OpenSpec content: configuration, source
  specifications, in-flight changes, and shared templates

## Conditional UX stage

UX design and UX validation apply only to changes affecting a visual interface.
Product Owners record this in the existing accepted proposal:

````markdown
## UX Applicability

```json
{"required": false, "reason": "CLI-only change; no visual interface is affected."}
```
````

Nonvisual CLI, API, and framework changes go directly to architecture. They need
no UX brief, UX-specific specs, UX validation report, UX tests, or frontend
tooling. Their functional specs, tests, coverage, security, and other applicable
gates remain required. Mixed changes scope UX to affected visual surfaces.
Missing or conflicting applicability requires clarification, not a default.

Visual changes go through the UX Designer before architecture and preserve
criterion IDs through design and QA validation. See the
[UX design skill](.github/skills/ux-design/SKILL.md) and
[QA skill](.github/skills/test-generation/SKILL.md).

Before an existing proposal's next design/test handoff, add its scope-backed
applicability section and obtain acceptance. An old missing declaration is not
an automatic exemption, but nonvisual proposals need no new UX documents.

Visual consumers configure `UX_CHECK_NAMES` as a JSON list of unique check-run
names from their own PR-triggered UX workflows, for example
`["Browser UX", "Accessibility"]`. QA maps brief criteria to actual results in
`ux-validation.json`. The test-completion and security-entry gates require the
named checks to succeed for the evaluated PR head; they wait up to five minutes
for pending checks and fail clearly on timeout. Coverage alone is not UX proof.
No UX configuration or report is required for nonvisual changes.

Adopt the updated orchestrator together with the test-generation skill and its
bundled Python helper. The example consumer manifest protects the orchestrator,
so review and apply its changes explicitly when that protection is retained.
Keep existing functional test setup; the shared workflow's normal Python/.NET
commands are unchanged. Consumer UX suites remain in consumer-owned CI rather
than a universal shared browser runner.

## Markdown validation

Lint every tracked Markdown file from the repository root:

```powershell
$files = git ls-files -- "*.md"
npx markdownlint-cli2 @files
```

The Markdown lint configuration requires 80-column prose but exempts code blocks
and tables to preserve runnable commands and readable reference examples.

## Consumption model

Most of these assets are **repository content**, not reusable `workflow_call`
modules. Consumer repositories should **sync** compatible shared files from this
repository instead of editing divergent local copies. Asset synchronization and
OpenSpec store selection are complementary mechanisms:

- **Synchronization** distributes shared agents, skills, instructions,
  workflows, issue templates, and optional specification content through a
  reviewed pull request.
- **A consumer OpenSpec store** owns that consumer's product specifications and
  active changes. Command skills use the nearest local `openspec/` root by
  default.
- **The shared OpenSpec store** owns this repository's shared specifications and
  changes. Consumer feature work must not be created in the shared store.

Recommended pattern:

1. Edit shared artifacts here.
2. Sync them into consumer repositories through automation PRs.
3. Keep product-specific code, infrastructure, runtime docs, source
   specifications, and active OpenSpec changes in the consuming repo.

## Consumer manifest

This canonical source repository includes `.agentic-shared.yml` with every asset
group set to `local`, so default manifest validation works without synchronizing
the source repository against itself. Its release pin is a reference baseline,
not a claim that the current worktree matches that release.

Consumer repositories should copy `.agentic-shared.example.yml` to
`.agentic-shared.yml` and pin a tagged release. The manifest declares which
asset groups are shared and whether each group is `managed`, `extended`, or
`local`.

The supplied example sets `assets.specs: local` and protects
`openspec/changes/**`. This is the recommended consumer configuration: consumers
keep their OpenSpec store local while receiving the shared Fabric skills and
SDLC policy assets. Set `assets.specs` to `managed` or `extended` only when
deliberately adopting shared `openspec/` content and reviewing the resulting
configuration and spec updates.

Validate a manifest before opening a synchronization PR from the repository
root:

```bash
python .github/scripts/validate_agentic_shared_manifest.py .agentic-shared.yml
```

Copy `.github/workflows/agentic-shared-sync.yml` into the consumer repository.
Run it manually with a tagged `target_version`. It checks out the installed and
target releases, performs a three-way update, and opens a pull request. A
managed-path conflict fails the workflow before any consumer file is changed.
Removal of a formerly shared `openspec-*` skill or collision with a
consumer-owned skill also stops synchronization for reviewed migration;
protected paths remain untouched.
New releases exclude upstream `openspec-*` skills from Fabric synchronization.
Migration of an unchanged formerly shared skill requires an explicitly reviewed
hash-bound migration record and generated upstream replacements, supplied via
`--openspec-migration <review.json> --upstream-source <generated-root>` to the
synchronizer. Customized, consumer-owned, or protected copies are not silently
replaced. See the [migration procedure](doc/fabric-consumer-migration.md) for
review fields, replacement checks, and backup-based rollback.

Use reserved `local/` directories for consumer-only extensions:

- `.github/agents/local/`
- `.github/skills/local/`
- `.github/prompts/local/`
- `.github/instructions/local/`

Software Fabric workflows are maintained as `fabric-*` command skills under
`.github/skills/`. Upstream-generated `openspec-*` skills are installed and
updated by OpenSpec, not synchronized as Fabric-owned assets.
Consumer-owned prompts may remain under
`.github/prompts/local/`; shared prompt wrappers are no longer published.

Consumer changes to shared behavior should be proposed here through an issue or
OpenSpec change. Consumer-specific behavior belongs in a local extension path
and must not edit synchronized files in place.

## OpenSpec and Software Fabric entry points

OpenSpec owns CLI mechanics, schemas, artifact paths, and upstream-generated
skills. Fabric owns persona handoffs, acceptance, intake, and applicable quality
gates in separately named skills. Existing consumers default to Fabric; an
explicit standalone OpenSpec selection uses the upstream skills unchanged,
without Fabric agent orchestration. Repository merge and release controls remain
independent of mode.

| Action | Fabric chat skill | Standalone OpenSpec chat skill |
| --- | --- | --- |
| Proposal/planning | `/fabric-propose` | `/openspec-propose` |
| Apply | `/fabric-apply-change` | `/openspec-apply-change` |
| Verify | `/fabric-verify-change` | `/openspec-verify-change` |
| Sync | `/fabric-sync-specs` | `/openspec-sync-specs` |
| Archive | `/fabric-archive-change` | `/openspec-archive-change` |
| Bulk archive | `/fabric-bulk-archive-change` | `/openspec-bulk-archive-change` |

Other actions use the same `fabric-` versus `openspec-` prefix. Report the route
with `python .github/skills/fabric-propose/scripts/route_fabric_workflow.py --action apply`;
add `--mode standalone` only after an explicit standalone selection. This reports
advisory routing; it neither changes repository protection nor proves approval.
The mode and explicitly selected store remain sticky through handoffs.

These chat workflows are not terminal commands. For example,
`openspec instructions apply --change <slug> --json` supplies upstream task
instructions; Fabric apply additionally verifies accepted complete planning.
Fabric archive requires all applicable gates and every-delta sync verification.
Direct `openspec archive <slug>` does not enforce the Fabric checklist, nor can
agent instructions prevent arbitrary local CLI writes. Configured trusted checks
and administrator protections govern merge and release destinations separately.
See [Fabric policy](.github/instructions/fabric-workflow.instructions.md),
[gate evidence](doc/fabric-gate-evidence.md), and
[reviewed migration](doc/fabric-consumer-migration.md).

Initially Fabric supports exactly OpenSpec **1.16.0** and Node.js **26 or later**.
This is Fabric's tested runtime baseline; the OpenSpec 1.16.0 npm package declares
Node.js `>=22.12.0`. Unsupported integration versions fail compatibility checks;
expanding support requires upstream diff
review and passing version-specific tests.

### Consumer-local store (recommended)

Consumers that use the command skills require Node.js 26 or later and the
OpenSpec CLI. Initialize or retain an `openspec/` root in the consumer
repository:

```powershell
npm install -g @fission-ai/openspec@1.16.0
openspec init
openspec context --json
openspec doctor
```

Run `openspec init` in the consumer repository and retain its existing
`openspec/` configuration. `openspec context --json` must resolve the
repository's OpenSpec root before a command skill can create or modify
artifacts. The skills then use that nearest local root, so consumer proposals,
delta specs, and changes remain consumer-owned.

### Shared store (explicit selection)

OpenSpec stores are standalone OpenSpec repositories registered on a developer
machine; they are not a replacement for the synchronization workflow. To inspect
the shared store from a local clone, register it and select it explicitly:

```powershell
openspec store register <path-to-agentic-shared> --id agentic-shared --yes
openspec store list --json
openspec context --json --store agentic-shared
```

After selecting a store, pass `--store agentic-shared` to subsequent OpenSpec
commands that read or modify specs and changes, for example:

```powershell
openspec list --json --store agentic-shared
openspec validate --all --json --store agentic-shared
```

Use the shared store to inspect or maintain shared SDLC content in this
repository. Use a consumer-local store for consumer product work; do not create,
apply, or archive consumer changes in the shared store.

## Current consumers

| Repository               | Relationship                                                                          |
| ------------------------ | ------------------------------------------------------------------------------------- |
| `ralphke/Agentic-Coding` | Full Software Fabric consumer; syncs the complete shared agentic SDLC content set     |
| `ralphke/Agentic-DevOps` | Selective consumer; keeps Azure, pipeline runtime, and local OpenSpec content in-repo |

## Notes on compatibility

`Agentic-Coding` already matches the shared `openspec/` conventions, so it can
consume the full content set directly.

`Agentic-DevOps` currently uses `openspec/`, so it adopts the shared content as
those paths are aligned.

## Update policy

- Treat this repository as the canonical home for shared agentic assets.
- Pin consumers to tagged releases rather than a moving branch.
- Deliver updates through consumer pull requests so local CI and human review
  run before merge.
- Managed-path conflicts must fail closed; never overwrite consumer changes
  automatically.
- Avoid editing synchronized files directly in consumer repositories unless the
  change is immediately promoted back here.

### Mandatory Software Fabric gates

Ideas and draft proposals have an early **Proceed / Defer / Do not pursue**
decision before any repository capture write, including initialization and
scaffolding. Assess in conversation or session storage outside the worktree.
Raw ideas, labels, P0 priority, and kickoff do not authorize capture; an explicit
request to create named repository artifacts counts as Proceed without another
prompt at handoff. Missing input keeps capture paused.

Defer or rejection needs no delivery gates and leaves repository files untouched.
It is not successful archive or task completion and never deletes existing work;
cleanup of an already captured proposal needs separate explicit authorization.
Proceed authorizes capture only, not acceptance of the resulting proposal/spec.

Implementation requires complete proposal, delta specs, design, and ordered
tasks plus explicit acceptance of the current proposal/spec. Existing
conversation approval or linked review can supply acceptance evidence; file
existence and CLI readiness alone cannot. Skipped required artifacts or a schema
omitting a required role block readiness rather than waive it.

Single and bulk archive require complete required artifacts/tasks and verifiable
passing evidence for every mandatory quality gate in
`.github/instructions/openspec-workflow.instructions.md`. User confirmation
cannot override mandatory gates. Every delta of an archived change must be synced
and verified in the main specs; a blocked delta blocks its whole change.
Genuinely optional artifacts keep informative warnings.

The conventional-path `validate_openspec_change.py` checks local planning files,
delta presence, and usable completed task checkboxes. It does not certify
substantive planning acceptance, scenario coverage, external CI, review, security,
legal or operational gates, or completed spec sync. The archive-readiness workflow
also checks PR evidence only when a PR is supplied; a green run is not complete
Software Fabric archive clearance.

### After updating the OpenSpec CLI assets

Fabric policy is never restored into upstream skill bodies. The former
`restore_openspec_contracts.py` tool is retired. Fabric retains its gates in
separate skills; upstream may legitimately permit a different workflow.

1. Preserve worktree edits and record `node --version` and `openspec --version`.
   Before any `openspec init`, back up existing configuration; do not initialize
   an already configured root to refresh skills.
2. Review proposed upstream skill changes in an isolated project. The canonical
   snapshots use OpenSpec's custom profile with all twelve workflows and
   skills-only delivery for GitHub Copilot. Configure this only in the isolated
   project's `XDG_CONFIG_HOME` (`profile: custom`, `workflows`: the selected
   actions, `delivery: skills` in `openspec/config.json`), not by overwriting a
   developer's global profile. Consumers may retain their upstream tool/profile.
3. Adopt a version only after updating the declared compatibility set and
   pinned CI version with reviewed evidence. Run `openspec update` on the
   intended upstream assets; review `git diff -- .github\skills`. Never patch
   Fabric policy back into upstream skills or overwrite consumer customizations.
4. Run targeted and full validation with bytecode disabled:

   ```powershell
   $env:PYTHONDONTWRITEBYTECODE = "1"
   python -m unittest discover -s .github\scripts -p "test_openspec_command_skills.py"
   python -m unittest discover -s tests -p "test_fabric_skill_ownership_cli.py"
   python -m unittest discover -s .github\scripts -p "test_*.py"
   openspec context --json
   ```

PyYAML is the shared script suite's existing dependency; install it only when
missing. The ownership integration test generates all upstream skills and runs
a real refresh in an isolated project, comparing upstream bytes and verifying
Fabric files remain unchanged. Contract tests separately check Fabric policy;
they are not runtime proof of an agent's future compliance.
OpenSpec-derived skill material retains its
[MIT notice](doc/openspec-LICENSE.txt).
Pull-request CI must not repair the checkout before testing. The
`Shared script contracts` job runs only in `ralphke/agentic-shared` and
skips consumer repositories, which do not receive this repository's script tests
through asset synchronization. Administrators must configure the shared-script
test check as required in branch protection separately.
