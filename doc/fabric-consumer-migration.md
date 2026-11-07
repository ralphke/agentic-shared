# Consumer migration: separate Fabric from OpenSpec

## Ownership and supported baseline

Fabric remains the default for existing consumers. Move Fabric chat invocations
from `/openspec-<suffix>` to `/fabric-<suffix>`:

| Former Fabric invocation | Separated Fabric invocation |
| --- | --- |
| `/openspec-propose` | `/fabric-propose` |
| `/openspec-apply-change` | `/fabric-apply-change` |
| `/openspec-archive-change` | `/fabric-archive-change` |
| `/openspec-bulk-archive-change` | `/fabric-bulk-archive-change` |
| `/openspec-continue-change` | `/fabric-continue-change` |
| `/openspec-explore` | `/fabric-explore` |
| `/openspec-ff-change` | `/fabric-ff-change` |
| `/openspec-new-change` | `/fabric-new-change` |
| `/openspec-onboard` | `/fabric-onboard` |
| `/openspec-sync-specs` | `/fabric-sync-specs` |
| `/openspec-update-change` | `/fabric-update-change` |
| `/openspec-verify-change` | `/fabric-verify-change` |

Upstream owns generated `.github/skills/openspec-*` files; shared sync excludes
them from the **new** release inventory, even when they exist in that release's
checkout. The **old** release inventory still identifies formerly shared files.
Fabric owns separately named entry points and policy; do not restore Fabric
policy into upstream skill bodies. Explicitly select standalone OpenSpec for
standalone work. Terminal commands such as `openspec archive` are not chat
invocations and do not enforce Fabric gates. Repository merge/release controls
remain independent of mode selection.

The supported integration is exactly **OpenSpec 1.16.0** with Fabric's
**Node.js 26+** baseline. This is Fabric's support policy, not a claim about
OpenSpec's own minimum runtime. Verify the official npm package
`@fission-ai/openspec` before installing `@fission-ai/openspec@1.16.0`;
do not use `@latest` for migration or compatibility evidence.

## Prepare a reviewed migration (no live consumer edits)

1. Use a disposable clone/branch of the consumer and immutable checkouts of its
   prior pinned shared release and the target release. Back up the consumer
   manifest and the exact formerly shared skill bytes outside the worktree.
   Preserve local extensions, config, specs, and active changes in the backup.
2. Generate upstream skills with the supported CLI in a **separate temporary
   project**. Isolate `HOME`, `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`,
   `XDG_CONFIG_HOME`, and `XDG_DATA_HOME` to temporary directories; set
   `OPENSPEC_TELEMETRY=0` and `CI=1`. Do not run init/update against the consumer
   just to obtain replacement bytes.
3. Check `openspec --version` is `1.16.0`. Run
   `openspec init --tools github-copilot --no-copilot-cloud` in that temporary
   project. Its configured workflow profile determines generated actions.
   Use `openspec config profile` in the isolated environment to select the
   required actions, then `openspec update`. A core-only profile may not supply
   all twelve replacements; missing files must block, not be invented.
4. Review every former file against the old release and consumer, upstream
   replacements, and the target Fabric entry points. Review invocation changes
   and handoffs as well as content. Record one JSON entry per retired file,
   including auxiliary files. Compute SHA-256 over the **actual bytes**, not
   normalized text. `Get-FileHash -Algorithm SHA256 <file>` (lowercase its output)
   or `sha256sum <file>` can supply the hashes.
5. Have the migration reviewed in the consumer PR. Keep a reviewer identity and
   a durable review reference in the JSON. These fields are an audit pointer,
   not an authenticated approval service: operators must verify the linked
   review. A boolean confirmation alone cannot authorize migration. Keep
   secrets and personal/sensitive review content out of the file.

Example `review.json` (replace placeholders with reviewed values):

```json
{
  "schema_version": 1,
  "repository": "ralphke/agentic-shared",
  "from_version": "v1.0.3",
  "to_version": "v2.0.0",
  "openspec_version": "1.16.0",
  "reviewed_by": "reviewer-handle",
  "review_reference": "consumer-pr-review-reference",
  "files": [
    {
      "path": ".github/skills/openspec-propose/SKILL.md",
      "sha256": "<64 lowercase hex characters: old and unchanged consumer bytes>",
      "replacement_path": ".github/skills/openspec-propose/SKILL.md",
      "replacement_sha256": "<64 lowercase hex characters: upstream bytes>",
      "fabric_path": ".github/skills/fabric-propose/SKILL.md",
      "fabric_sha256": "<64 lowercase hex characters: effective Fabric bytes>"
    }
  ]
}
```

`repository` binds to `source.repository`; release versions bind to the current
manifest and requested target. The review must cover all present, unprotected
formerly shared OpenSpec files being retired, without duplicate entries.
Replacement paths can differ when upstream renames a skill. Each replacement
must be in an upstream `openspec-*` skill with an available `SKILL.md`.
Each Fabric path must identify an available `.github/skills/fabric-*/SKILL.md`,
either scheduled by this sync or already installed with matching bytes.
Hashes bind review to those exact bytes; re-review after any content change.

Run from the disposable consumer checkout, using the target release's scripts:

```powershell
python -B <shared-new>/.github/scripts/sync_agentic_shared.py `
  --manifest .agentic-shared.yml `
  --old-source <shared-old> --new-source <shared-new> `
  --destination . --target-version v2.0.0 `
  --openspec-migration <review.json> --upstream-source <generated-project>
```

Python needs the existing PyYAML dependency. Both migration options are required
together. The library interface is
`synchronize(manifest, old_root, new_root, destination_root, target_version,
migration_review=None, upstream_root=None)`; it returns changed relative paths.

Without review, retirement blocks. With review, only byte-identical formerly
shared files can be replaced/retired. Customized, consumer-owned, or protected
files cannot be overridden by this input. Existing replacement files must
already match upstream bytes unless they are the unchanged retired file.
Protected files remain unchanged; an explicitly listed protected file blocks
the review. Preserve customized skills for a separate manual ownership review,
not by substituting their hash into the migration record.

All migration checks and ordinary three-way conflicts are evaluated before
copies/deletions or manifest version updates. Missing replacements/Fabric
entries, stale hashes, invalid paths, or conflicts leave the worktree and
version unchanged. Filesystem failures during the subsequent writes are not
transactionally rolled back; use the disposable clone and backup to recover.
Do not mutate inputs concurrently with sync.

The standard automatic sync workflow intentionally has no blind migration
confirmation: it blocks retirement until this reviewed migration is performed.
Inspect the complete diff, test invocations, and merge a reviewed consumer PR.
Subsequent releases no longer own upstream skills and need no migration input.

## Recommended manifest and store verification

Keep the existing `.agentic-shared.example.yml` ownership modes, especially:

```yaml
assets:
  skills: extended
  specs: local
protected_paths:
  - .github/skills/local/**
  - openspec/changes/**
```

This is an excerpt, not a replacement for the complete example: retain its
other asset groups and protected local extension/workflow paths. `specs: local`
skips all shared OpenSpec config, specs, and changes. Do not switch it to managed
to obtain skills; skills have a separate asset root.

From a consumer project, `openspec context --json` resolves the local project.
`openspec new change <product-change>` writes to its local `openspec/changes/`.
Register a shared store only when needed:

```powershell
openspec store register <shared-store-path> --id agentic-shared --yes
openspec context --json --store agentic-shared
openspec new change <shared-change> --store agentic-shared
```

Pass `--store agentic-shared` on each applicable command for shared work.
Registration/explicit selection does not change the default for later commands
without that option. Do not move consumer product data into the shared store.
Tests use isolated `store setup --no-init-git`, not a real consumer/shared store.

## Updates and rollback

Before adopting another OpenSpec version, review the upstream generated skill
diff and pass compatibility tests for the proposed version. Expand the supported
set explicitly; a version claim in review JSON is not executable verification.
After migration, update upstream skills through OpenSpec separately from Fabric
sync and review the resulting diff. Back up and restore repository-specific
`openspec/config.yaml` fields if any subsequent init/update changes them.

Rollback is a **reviewed consumer PR**, not automatic deletion of new files:

1. Restore the prior pinned `.agentic-shared.yml` and formerly shared skill
   bytes from the pre-migration backup. For an unmerged disposable branch,
   discard only that branch/clone and retry from the backup.
2. For a merged migration, compare every affected file with the migration
   result. Restore only files still matching that result; later customizations
   require conflict review. Remove a newly introduced replacement/Fabric file
   only if it remains unchanged and the rollback review approves removal.
3. Review the ordinary three-way sync back to the prior shared release for
   other shared assets. The new sync selector never redistributes `openspec-*`,
   even on rollback: restore those legacy files explicitly from the reviewed
   backup rather than weakening upstream ownership or collision checks.
4. Never reset the whole consumer worktree or replace its OpenSpec store.
   Keep local extensions, product specs, config, active changes, and subsequent
   consumer edits. Re-test the prior invocations before merging.

## Reproducible checks

With OpenSpec 1.16.0 installed, from the shared repository:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python -B -m unittest discover -s .github/scripts -p test_sync_agentic_shared.py
python -B -m unittest discover -s .github/scripts -p test_openspec_skill_migration.py
python -B -m unittest discover -s .github/scripts -p test_fabric_migration_store_cli.py
```

The store test exercises the real CLI in an isolated project/config/data
registry. It skips explicitly if no CLI exists; a skip is not store validation.
The sync tests load the real recommended manifest and verify preserved local
product data, successful replacement, missing-replacement failure, protected
paths, collisions, review binding, and unchanged version on preflight failure.
