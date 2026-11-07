# Fabric and OpenSpec guidance quality

## Baseline

The following baseline captures the guidance before separating Fabric from
OpenSpec. Reassess the corresponding replacement entry points and instruction
file using the same rubric after implementation.

Each dimension scores 1 when the stated evidence is present and 0 otherwise:

- **Ownership:** identifies upstream OpenSpec behavior separately from
  Fabric-owned policy and entry points.
- **Structure:** provides identifiable purpose and workflow sections.
- **Execution:** provides actionable steps and explicit stop conditions.
- **Handoff:** identifies the next action or approval boundary.

| Sample | Ownership | Structure | Execution | Handoff |
| --- | --- | --- | --- | --- |
| `.github/skills/openspec-propose/SKILL.md` | 0 | 1 | 1 | 1 |
| `.github/skills/openspec-apply-change/SKILL.md` | 0 | 1 | 1 | 1 |
| `.github/instructions/sdlc-fabric.instructions.md` | 0 | 1 | 1 | 1 |

The two `openspec-*` samples include Fabric policy inside upstream-named skill
files. The Fabric instruction file does not describe standalone OpenSpec
selection or distinguish that mode from Fabric-managed work. All three define
purpose or workflow sections, actionable rules, and handoff or approval
boundaries.

## After ownership separation

The same binary rubric is applied to the Fabric replacements, not to upstream
skills whose independent workflow is intentionally retained.

| Baseline sample's replacement | Ownership | Structure | Execution | Handoff |
| --- | --- | --- | --- | --- |
| `.github/skills/fabric-propose/SKILL.md` | 1 | 1 | 1 | 1 |
| `.github/skills/fabric-apply-change/SKILL.md` | 1 | 1 | 1 | 1 |
| `.github/instructions/sdlc-fabric.instructions.md` | 1 | 1 | 1 | 1 |

- **Proposal:** the purpose/trigger and invocation boundary name Fabric-default
  and explicit standalone behavior. The numbered workflow specifies
  compatibility, resolved-root and intake stops, then proposal acceptance,
  conditional UX, architecture, and a separate implementation request.
- **Apply:** the invocation boundary names its unchanged upstream counterpart.
  The purpose, numbered steps, missing-acceptance stops, exact task updates,
  and verification/archive handoffs retain the previous execution contract.
- **Fabric instructions:** the Work Mode section scopes persona/stage rules to
  Fabric, identifies unchanged repository controls in both modes, and provides
  the advisory selector. The pipeline, rules, and named skill handoffs remain.

Each sample improves ownership from 0 to 1 (3/4 to 4/4 total); the other three
dimensions remain 1. These are guidance-quality observations, not automated
proof of agent compliance or clearance of lifecycle gates. The installed-CLI
ownership test independently verifies generated upstream content and that a
real upstream refresh leaves Fabric assets intact.

## Validation checkpoints

Before the accepted different-revision mapping refinement and merge-control
security fixes, with `PYTHONDONTWRITEBYTECODE=1`:

| Command | Observed result |
| --- | --- |
| `python -m unittest discover -s .github\scripts -p 'test_*.py'` | 148 tests, passing with one Windows symlink-privilege skip |
| `python -m unittest discover -s tests -p 'test_*.py'` | 84 tests passed |
| `openspec validate separate-fabric-from-openspec --strict --json` | Change valid; no issues |

The ownership CLI test includes real isolated upstream generation and refresh.
Other gate tests use API fixtures; they do not establish live GitHub
permissions, rulesets, or environment protection. This checkpoint is not final
verification of the subsequent mapping and security changes.

After implementing the accepted mapping and both merge-control fixes:

| Command | Observed result |
| --- | --- |
| `python -m unittest discover -s .github\scripts -p 'test_*.py'` | 171 tests, passing with one Windows symlink-privilege skip |
| `python -m unittest discover -s tests -p 'test_*.py'` | 84 tests passed |

The shared suite includes the 72 gate/mapping tests, migration tests, and
separate Fabric/upstream policy contracts. Gate scenarios cover merge, release,
and archive, authorized different-revision mapping, malformed or missing
sources, expiry, mutable-link rechecks, protected source identity, explicit
controlled merge, and missing operational evidence before mutation. The final
security review and administrator setup remain separate from these local test
results; no live merge, release, deployment, or archive was performed.

Python SAST used Bandit 1.9.4 installed in a new session-only virtual environment,
after the existing Python reported that Bandit was unavailable. No repository
dependency manifest or shared Python installation was changed. The scan used
`-r` on `fabric-verify-change/scripts`, `fabric-propose/scripts`,
`software-fabric-kickoff/scripts`, `sync_agentic_shared.py`, and
`openspec_skill_migration.py`, with `-ll -f json`: exit 0, 1,642 lines scanned,
no scan errors, and no MEDIUM/HIGH findings. This does not replace workflow
security scanning or verification of live repository protections.

After fixing the mapped-archive merged-state finding:

| Command | Observed result |
| --- | --- |
| `python -m unittest discover -s .github\scripts -p 'test_*.py'` | 174 tests, passing with one Windows symlink-privilege skip |
| `python -m unittest discover -s tests -p 'test_*.py'` | 84 tests passed |

This is 257 passed tests and one skip. The same isolated Bandit command was
rerun after the fix: exit 0, 1,643 lines scanned, no scan errors, and no
MEDIUM/HIGH findings.

## Security review outcome

The local review covered the seven gate runtime/schema/policy files, four gate
test files, three lifecycle workflows, gate documentation, and trusted archive
hooks. The earlier routing/migration review reported no vulnerabilities.

| Finding | Severity | Resolution |
| --- | --- | --- |
| Shared Actions-token verdict spoofing | MEDIUM | Unique gate-App provenance, credential-custody prerequisites, and exclusive controlled-destination checks |
| Persistent success after expiry or withdrawal | MEDIUM | Fresh evaluation and expected-head conditional merge; scheduled revocation remains supplemental |
| Unmerged PR accepted by different-revision archive mapping | MEDIUM | Independent merged-state assertion at initial and final archive checks, without changing evaluated/head-SHA matching |

The reviewer confirmed all three findings closed in the local implementation.
For the last fix, the reviewer independently verified the three changed files,
ran 11 mapping tests and scoped Ruff, and reported no remaining high-confidence
findings. The developer's full focused gate run passed 75 tests and 75 subtests.
Regressions cover initial/final unmerged rejection, valid mapping with three
distinct SHAs, and open-PR pre-merge evaluation.

This closes the implementation review, not a live security gate. The refreshed
integrated tests and SAST above are separate parent verification; the missing
administrator and lifecycle evidence below remains blocking.

## Legal-risk assessment

The accepted scope changes shared governance assets, synchronization helpers,
and evidence controls, not a product application or database. No product
datasets, regulated-data integrations, or application runtime dependencies
were introduced. The evidence contract retains references rather than secrets
or copied review content. Redistributed upstream material retains its MIT
notice in [openspec-LICENSE.txt](./openspec-LICENSE.txt), with a distributed copy
under the Fabric proposal assets.

No mandatory legal escalation is identified for this shared-asset scope.
This is not legal advice or clearance of a consumer's deployment: consumers
must reassess evidence-data handling, external mapping producers, credentials,
and third-party rights against their own environment and obligations. Any new
legal-risk trigger requires the Legal & Compliance stage before release.

## Administrator handoff and remaining evidence

Before using these controls in a target repository, administrators must:

1. Configure a unique gate App and require the merge check from that exact App,
   not a same-named result from the shared GitHub Actions token.
2. Isolate App credentials in the protected gate environment and establish
   independently verifiable credential-custody prerequisites.
3. Configure exclusive controlled merge permissions and protected destinations;
   identify bypass actors and independently authorized tag/release writers.
   The controlled release job cannot prohibit every direct release API call.
4. Configure exact authorized check, review, disposition, operational, and
   mapping producers, explicit implementation/deployment repositories, and
   appropriate freshness/expiry limits.
5. Protect the evaluator/policy base and verify the complete setup with
   authenticated evidence before permitting controlled operations.

Live App identity, protections/rulesets, environment isolation, credential
custody, destination exclusivity, mapping-provider behavior, and actual
lifecycle evidence were not configured or verified in this implementation.
Unsupported or unverifiable setup remains blocking; local tests and SAST do
not supply that evidence. External reads and merge processing are not
transactional, and scheduled revocation does not give checks a TTL.

Semgrep, Gitleaks, pip-audit, pip-licenses, actionlint, zizmor, and CodeQL were
unavailable for this review. No live merge, release, deployment, archive,
consumer migration, or repository-protection change was performed. Completing
implementation tasks is not merge, release, or archive clearance; obtain all
applicable external quality-gate evidence separately.
