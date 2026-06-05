# Skill: Workflow Retrospective and Improvement

**Description**
- **USE FOR:** deriving workflow and skill improvements from real issue/PR history, then turning that into concrete updates for `.github/workflows/` and `.github/skills/`.
- **DO NOT USE FOR:** implementing product features, replacing incident response, or making policy changes without maintainer approval.

**Persona:** Operations SRE Agent
**Input:** repository issues, pull requests, labels, review outcomes, workflow runs
**Output:** prioritized improvement report + proposed changes to skills/workflows

---

## When to Use & Triggers

Use this skill when:
- Weekly or monthly process review is due
- A recurring failure pattern appears across issues/PRs
- Cycle time, review quality, or stage handoff quality drops
- A maintainer requests SDLC process hardening

Do not trigger when:
- There are no process signals to analyze and no workflow/skill change request
- The request is strictly feature delivery

---

## Workflows & Steps

1. **Collect history window** — last 30/60/90 days of issues and PRs.
2. **Compute core signals** — merge lead time, stage-label coverage, blocked/security outcomes, reopen rate.
3. **Detect repeated friction** — identify top 3 failure modes by frequency and impact.
4. **Map to root causes** — decide whether each issue is skill guidance, workflow automation, or governance.
5. **Draft improvements** — produce concrete edits with owner and expected impact.
6. **Apply changes in branch** — update skills/workflows with minimal, testable deltas.
7. **Publish report and PR** — include evidence table, proposed changes, and rollback plan.

---

## Scripts & Tools

```bash
# Issues / PR history
gh issue list --state all --limit 100 --json number,title,state,labels,createdAt,closedAt,url
gh pr list --state all --limit 100 --json number,title,state,labels,createdAt,mergedAt,closedAt,url

# Review quality samples (per PR)
gh pr view <number> --json reviews,comments,labels,files,commits

# Workflow outcomes
gh run list --limit 100 --json name,status,conclusion,createdAt,updatedAt,workflowName,url
```

---

## Rules & Guidelines

- Prioritize **high-frequency + high-impact** friction first.
- Keep recommendations evidence-based; no generic best-practice-only changes.
- Prefer additive, reversible changes over broad rewrites.
- Never merge process changes directly to `main` without human approval.
- Keep skill docs concise and executable.

---

## Error Handling

| Error | Likely Cause | Fix |
|---|---|---|
| Empty issues/PR results | New repo or little activity | Emit baseline recommendations and add instrumentation-oriented workflow checks |
| API throttling/auth failure | Missing `gh` auth or rate limits | Re-authenticate `gh`, reduce query scope, retry with smaller windows |
| Noisy/unlabeled data | Inconsistent label usage | Add label hygiene recommendation and automation in workflow |
| Conflicting recommendations | Multiple root causes overlap | Rank by impact and ship in small, ordered changes |

---

## Scenarios & References

- **Sparse-history repo:** bootstrap with conservative defaults and establish measurement loop.
- **High security rework:** strengthen `stage:security` gates and remediation requirements.
- **Slow review throughput:** tighten review expectations and automate handoff comments.

Reference sources:
- `.github/workflows/*.yml`
- `.github/skills/*.md`
- `spec/openspec/templates/Skills.md`

---

## Quick Reference

| Task | Command |
|---|---|
| Pull issue history | `gh issue list --state all --limit 100 --json number,title,state,labels,createdAt,closedAt,url` |
| Pull PR history | `gh pr list --state all --limit 100 --json number,title,state,labels,createdAt,mergedAt,closedAt,url` |
| Inspect one PR deeply | `gh pr view <number> --json reviews,comments,files,labels` |
| Inspect workflow failures | `gh run list --limit 100 --json workflowName,status,conclusion,url` |

---

## Collaboration & Iteration Loop

1. Analyst/agent proposes changes with evidence.
2. Maintainer reviews and adjusts scope.
3. Changes ship via PR with explicit non-merge policy until human approval.
4. Next retrospective validates whether metrics improved.

---

## Output Specs, Success, Evaluation & Security

**Output spec**
- Evidence summary table (signals + counts)
- Top 3 improvement actions
- Exact files to change with rationale

**Success criteria**
- Every recommendation maps to observed repository data
- At least one measurable metric is expected to improve
- Changes are scoped for safe human review

**Evaluation**
- Compare pre/post cycle-time and gate-pass trends
- Track reduction of repeated failure modes

**Security**
- Do not expose secrets or sensitive payloads in reports
- Keep analysis to repository metadata and approved artifacts
