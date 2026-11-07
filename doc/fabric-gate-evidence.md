# Fabric gate evidence and protected operations

Implements: `openspec/changes/separate-fabric-from-openspec/` tasks 3.1–3.6,
3.8, and the gate scenarios of 5.1. This does not constitute security approval,
proof of configured protections, or authorization to invoke live operations.

## Distributed files

Runtime is under `.github/skills/fabric-verify-change/scripts/`, distributed
by the skills asset group:

- `fabric_gate.py`: strict policy/manifest and lifecycle evaluation.
- `collect_fabric_evidence.py`: bounded live collector and archive preflight.
- `fabric_mapping.py`: external change/deployment mapping and linked snapshots.
- `fabric_control_policy.py`: exclusive App/environment prerequisites.
- `run_fabric_gate_control.py`: App verdicts, explicit operations and revocation.
- `gate-policy.json`, `gate-evidence.schema.json`: protected configuration/schema.

Canonical tests are `.github/scripts/test_fabric_gate*.py`.
Workflows are `.github/workflows/fabric-{merge,release,archive}-gate.yml`.
No new runtime dependency or general mapping platform is introduced.

**The shipped policy is deliberately unconfigured and fails closed.** App
IDs are zero and reviewer IDs are empty. Missing/disabled configuration,
unavailable services and missing applicability never mean non-applicable.

## Sources, applicability and substantive limits

Every lifecycle includes planning, current proposal/spec acceptance, required
task completion, passing new scenarios, CI, security, coverage, code review,
spec criteria and legal disposition. Release additionally evaluates release
readiness. Archive additionally evaluates deployment, SLOs, alerts, runbook,
completed stability window and required post-mortem.

Configured providers must actually certify the existing requirements: all
configured CI checks green, no HIGH/CRITICAL security findings, new-code
coverage at least 80%, authorized review, spec acceptance and applicable legal
and operational criteria. At archive all tasks must be complete. Planning
includes complete current artifacts and the accepted, scope-backed UX decision.
Missing UX/legal files are not an applicability decision.

The collector verifies authenticated identity, exact disposition, revision,
freshness and links—not the substantive truth of a provider's assessment.
Local structural validation is not security, legal or acceptance approval.

### Exact check and review sources

Checks select exactly one configured numeric App ID and exact name on the
required SHA. Completed success is required; missing, duplicate, stale,
skipped, neutral, pending, failed or unauthorized results block.

**GitHub Actions app/name alone is rejected.** PR-authored jobs can spoof names
under that shared App. A dedicated external provider may certify Actions
evidence only after independently validating protected producer workflow
identity/ref, revision and actor authorization. No direct Actions provenance
adapter is shipped. No PR artifacts/manifests are accepted as authorization.
Own `Fabric / merge`, `Fabric / release` and reserved archive identities cannot
be configured as source gates; the collector never waits on itself.

Review sources pin numeric reviewer IDs and current commit. Their latest
dispositions supersede older ones; self-review, dismissal, changes-requested,
wrong-commit and stale results block. Proposal/security/legal approvals require
the exact complete configured marker, respectively
`fabric-gate:acceptance:approved`, `fabric-gate:security:approved`, or
`fabric-gate:legal:approved`. Only code review permits a generic approval.
Review bodies are not copied into manifests.

### Trusted scope checks

Only coverage, legal, release readiness and operational/deployment gates permit
scope rules. Other gates cannot be waived. Optionality requires a separate
successful exact trusted scope check, bound to gate, revision and lifecycle;
archive also binds logical store/change identity.

Its JSON `output.summary` contains `gate`, `revision`, `lifecycle`, boolean
`required`, `scope_rule` and `reason`; archive adds `identity`. When required,
rule/reason must be null. Otherwise rule must exist in protected `allowed_rules`,
and reason must exactly equal its nonempty, non-sensitive configured description.
The provider must inspect actual scope. This prevents copied source content
leaking through the manifest. Exempting one gate never exempts another.

Evidence and scope timestamps are independently checked. Ages are between
1 and 86,400 seconds per configured gate; manifest age defaults to 900 seconds.
UTC is required, with at most 60 seconds future skew. A completed long stability
window needs a fresh observation, not permanently accepted ancient evidence.

## Archive hook and store identity

```text
python TRUSTED_ROOT/.github/skills/fabric-verify-change/scripts/collect_fabric_evidence.py --repository OWNER/CODE --lifecycle archive --revision EVALUATED_SHA --deployed-repository OWNER/DEPLOYMENT --deployed-revision DEPLOYED_SHA --store STORE --change SLUG --pr NUMBER --release-id ID
```

- `--repository` is the explicit evaluated code/evidence repository.
- `--deployed-repository` is mandatory and explicit, never inferred from a store.
- `--store local` identifies the canonical local planning root.
- `--store store:ID` identifies the selected registered store. Continue passing
  the original ID to OpenSpec; the prefix is the collector's namespace.
- Logical identity is `change:STORE:SLUG`; every archive check, including scope
  and mapping, must contain that exact `identity` in authenticated JSON summary.
- PR is explicit. Release ID is required for different revisions and whenever
  release/deployment is applicable. Trusted scope exemptions for both release
  readiness and deployment may permit absent release evidence on the same-SHA path.

The parent resolves actual planning roots through OpenSpec context/status,
keeps store selection sticky, checks planning/task completion and complete
delta verification separately, and runs this hook **immediately before each
archive-driven sync and again before move**. Each bulk item gets fresh evidence.
Nonzero/GateError blocks operations. Report partial writes; never claim rollback.
The collector does not write specs or move changes.

Python interface, imported only from the trusted runtime checkout:

```python
manifest = preflight(
    trusted_root, repository, "archive", evaluated_sha,
    f"change:{store_id}:{change_slug}",
    deployed_repository=deployed_repository, deployed_revision=deployed_sha,
    store=store_id, change=change_slug, pr_number=pr_number, release_id=release_id,
)
```

CLI prints externally generated JSON to stdout; it accepts no manifest/mapping
file. `validate_manifest` is structural/configuration validation, not proof of
provenance and never an authorization route for offline claims.

### Retrieve trusted runtime before executing Python

Read the explicit evaluated repository and its default branch through
authenticated `gh api --hostname github.com`; require `protected: true` and a
full current commit SHA. Verify the fetch remote identifies that repository,
fetch its default branch, and use a separate detached worktree:
`git worktree add --detach TRUSTED_ROOT BASE_SHA`.

Verify HEAD and clean runtime/policy files **before executing Python**.
Never execute a PR or selected-store copy. The collector independently checks
the current protected base before and after collection and validates final
freshness again. A moved base requires retrieval/reevaluation. A Python file
cannot securely authenticate itself after a caller has already executed a
modified copy. Runtime, policy, controller and workflows must be protected.

## Accepted different-revision mapping

Protected `mapping` configuration is null for same-SHA-only installations.
For different revisions configure an exact dedicated external App/check,
maximum age and explicit `repository_pairs` (`evaluated`, `deployed`).
Cross-repository same-SHA relationships also require explicit protected policy.
Store selection alone never authorizes a repository relationship.

One successful mapping check on EVALUATED_SHA supplies this strict record:

```json
{
  "schema_version": 1,
  "gate": "change_deployment_mapping",
  "identity": "change:store:planning:demo",
  "evaluated_repository": "owner/code",
  "evaluated_revision": "<full evaluated SHA>",
  "deployed_repository": "owner/deployment",
  "deployed_revision": "<full deployed SHA>",
  "pull_request": {
    "repository": "owner/code",
    "number": 123,
    "evaluated_revision": "<full evaluated SHA>"
  },
  "release": {
    "repository": "owner/deployment",
    "id": 456,
    "tag_object_sha": "<full tag/ref object SHA>",
    "commit_sha": "<full deployed SHA>"
  },
  "deployment": {
    "repository": "owner/deployment",
    "id": 789,
    "status_id": 790,
    "environment": "production",
    "revision": "<full deployed SHA>"
  },
  "observed_at": "<UTC timestamp>",
  "expires_at": "<UTC timestamp>"
}
```

Producer App identity, check ID/reference and completion timestamp come from
authenticated API responses, not record claims. Record lifetime cannot exceed
configured age. Missing, duplicate, expired, wrong-identity or unauthorized
mapping blocks before gate evaluation; ancestry and caller confirmation are
never queried or substituted.

The collector independently reads the PR, published release, tag/ref object,
peeled commit, deployment and latest successful status. Environment and exact
deployment/status creators must match protected deployment policy. It then
requeries mapping and mutable release/tag/status links before returning; changed
or superseded snapshots block. IDs identify objects but do not make release
content or tag pointers immutable. Manifests contain authenticated references,
timestamps and the mapping digest—not copied release/review content.

Mapped archive requires the linked PR to be merged at both initial preflight
and final recheck. Its head or merge commit must identify the evaluated SHA;
trusted mapping may still bind that evaluated SHA to a different deployed SHA.
The separate controlled pre-merge path continues to evaluate open PRs.

Change gates bind to evaluated SHA/repository. Operational gates bind to deployed
SHA/repository. Mapping grants no applicability exemption. The verified same-SHA
path remains: linked merged PR, published release/tag and current deployment
status are independently verified and rechecked without a mapping record.

## Actual controls and the two security boundaries

| Workflow | Actual identity/effect |
| --- | --- |
| Fabric Merge Gate | Gate-only App check **Fabric / merge** on current PR head; explicit protected merge operation |
| Fabric Release Gate | Gate-only App check **Fabric / release** on release SHA; gated unchanged-draft publication |
| Fabric Archive Gate | Read-only Actions job **Fabric archive preflight**, not an archive/move |

Verdicts are **check runs**, not shared-GITHUB_TOKEN commit statuses. Server
responses must identify the unique configured gate App, exact check ID/name and
SHA. A token named “gate” is not proof. Checkout uses read-only GitHub credentials;
privileged controller credentials are environment-only installation tokens.

### Administrator prerequisites (not configured here)

The supported protected merge path requires:

1. A unique gate-only App; installation token restricted to this one repository.
   Give only needed contents/checks/PR writes and prerequisite metadata reads
   (administration, environments and secret-name metadata). Unavailable API
   permissions block. No credential values enter manifests or logs.
2. Environment `fabric-gate-control` with custom branch policy allowing exactly
   the protected default **branch**, no tags/PR refs/wildcards, exact configured
   human reviewers and prevention of self-approval.
3. Short-lived `FABRIC_GATE_APP_TOKEN` only in that environment, provisioned by
   trusted administration outside PR workflows. Never place the App key/token
   in repository/organization secrets or duplicate it under another name.
   Named environment/repository/organization secret metadata is verified.
4. Because APIs cannot reveal undisclosed credential copies, an **independent
   trusted external custody check** on the current protected base is also
   mandatory. Its configured App must differ from the gate App. It certifies
   token custody and exclusive merge configuration, with a 900-second age bound:

   ```json
   {
     "repository": "owner/code",
     "base_revision": "<full protected base SHA>",
     "environment": "fabric-gate-control",
     "gate_app_id": 12345,
     "credential_isolation": "environment_only",
     "exclusive_app_merge": true
   }
   ```

   This is an administrator audit source, not self-certification by the token.
   Absent audit/provider evidence blocks; this change installs neither provider.
5. Classic branch protection: enforce admins, restrict users/teams to none and
   writers/mergers to only the gate App, require strict up-to-date **Fabric / merge**
   with that exact App ID, current code-owner review and dismissal of stale
   approvals, no PR bypass allowances, no force push/deletion. Disable native
   auto-merge; permit explicit squash merge. Protect runtime/config/workflow changes.
6. Active/inherited rulesets, merge queues or plans that cannot expose/enforce
   these exact restrictions are **unsupported and blocked**, not assumed safe.
   A separately accepted adapter is needed. Administrators must confirm their
   GitHub plan/repository supports these controls.

### Explicit merge boundary—not a timer-based TTL claim

Default `evaluate` publishes a verdict but **never merges**.
Only a deliberate workflow dispatch choosing `request-merge`, explicit PR and
full expected head, plus environment approval, requests a merge. The controller
validates prerequisites, evaluates evidence, then freshly repeats evaluation and
prerequisite checks in the same operation. It validates freshness at invocation
and calls GitHub's merge API with the expected head SHA. Native branch protection
and current native review rules are enforced by GitHub. A changed head, expired
evidence, withdrawn disposition, unavailable source or changed setup blocks.

Other writers/shared GITHUB_TOKEN cannot use an old successful verdict to merge
the destination because only the gate App is allowed to merge. This restriction,
not timestamps on a stored check, is essential. Only trusted default controller
code can consume the environment credential.

PR metadata changes, external check events, `fabric-evidence-changed` repository
dispatch and a five-minute sweep revoke checks; these paths never merge.
Configure trusted providers to dispatch on review submission/dismissal and other
evidence changes. Sweeps are bounded and subject to scheduling, approvals,
credential renewal and API failures. **They do not enforce instantaneous TTL.**
A stale check alone is not authorization through the exclusive protected path.

GitHub does not provide a distributed transaction across arbitrary external
evidence reads and merge processing. The implementation enforces a fresh,
head-conditional protected operation; it does not claim that every external
source is frozen during an in-flight API request. Administrators remain trusted
configuration/custody authorities. Independent security review is still needed.

### Release/publication boundary disclosure

The release job explicitly gates its own existing draft-release publication:
resolve tag, evaluate release SHA, recheck draft/tag/prerequisites, publish.
No release/deployment is invoked by implementing or testing this code.

Branch restriction does **not** prevent independently authorized repository
writers from calling GitHub's release API directly. Configure the intended
publication/deployment destination to accept only the gated path and restrict
other publication credentials. GitHub Releases has no equivalent universal
per-App branch protection for all independently authorized contents writers.
Do not claim this workflow prevents every direct release API call.
Immutable tags/restricted ref writers are required: ref checking and publication
are not transactional. A timed-out mutation can have an unknown remote outcome;
do not claim it rolled back or definitely did not publish.

## Bounds, validation and rollback

Reads/mutations share bounded request/deadline budgets: 80 requests, 120 seconds,
20 seconds per request, three pages of 100 records and 4 MiB per response.
Exhaustion, malformed/duplicate JSON or records, unavailable sources and ambiguous
applicability fail closed. Truncated collections never yield partial success.
No untrusted code is executed, no API error body/token is printed.

With `PYTHONDONTWRITEBYTECODE=1`:

```text
python -m unittest discover -s .github/scripts -p "test_fabric_gate*.py"
python -m pytest .github/scripts/test_fabric_gate.py .github/scripts/test_fabric_gate_mapping.py .github/scripts/test_fabric_gate_controls.py .github/scripts/test_fabric_gate_workflows.py -q
python -m ruff check .github/skills/fabric-verify-change/scripts .github/scripts/test_fabric_gate*.py
```

Tests are offline fixtures, not verification of live protections or provider
semantics. Retain generated evidence only in trusted logs/external storage.
Rollback runtime and policy together through reviewed pinned asset sync; do not
disable required controls or touch consumer specs as a rollback shortcut.
Direct OpenSpec CLI can still make local writes without Fabric preflight.
