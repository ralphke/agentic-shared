# Design: Add Legal Compliance Stage Gate

## Decision

Add a conditional `stage:legal` handoff to the SDLC orchestrator. Once a pull
request enters the legal stage, the workflow requires the explicit
`legal:approved` disposition before allowing `stage:review` or `stage:deploy`.
The `legal:blocked` disposition always rejects those downstream stages.

The workflow coordinates labels and comments only. The Legal & Compliance
Agent performs the review in Copilot and posts the assessment; qualified human
legal counsel remains responsible for any required legal sign-off.

## Label Contract

| Label | Meaning | Workflow behavior |
|-------|---------|-------------------|
| `stage:legal` | Legal review is required for this change. | Posts the legal-review handoff and disposition requirements. |
| `legal:approved` | Required legal assessment and any required counsel sign-off are complete. | Allows later review and deployment stages. |
| `legal:blocked` | A legal issue remains unresolved. | Fails review and deployment stage gates. |

Labels are applied manually by the responsible agent or reviewer. Automated
high-risk classification is out of scope; the Product Owner, Architect,
Security Engineer, or Legal & Compliance Agent may route a change to
`stage:legal` when legal-risk triggers are identified.

## Workflow Behavior

1. A reviewer applies `stage:legal` to a pull request requiring legal review.
2. The `stage-legal-gate` job posts the review instructions, assessment
   requirements, and disposition labels.
3. The Legal & Compliance Agent posts a Legal Risk Assessment and applies one
   of the documented dispositions.
4. An approved assessment applies `legal:approved` and then `stage:review`.
5. The review and deployment jobs read the current pull-request labels.
6. `legal:blocked` fails either job. A PR carrying `stage:legal` without
   `legal:approved` also fails either job.

## Decision Table

| `stage:legal` | `legal:approved` | `legal:blocked` | Review/deploy result |
|----------------|------------------|-----------------|----------------------|
| No | No | No | Allowed by legal gate |
| Yes | Yes | No | Allowed by legal gate |
| Yes | No | No | Blocked: missing disposition |
| Any | Any | Yes | Blocked: unresolved legal issue |

## Validation

Validate the workflow YAML locally, confirm all legal-stage and disposition
conditions are present, and run the OpenSpec archive-readiness validator. The
GitHub-hosted workflow must additionally be exercised on a pull request with
each decision-table label combination.

## Architecture Notes

### ADR-001: Use explicit disposition labels

A stage label states that a review is required but does not state its result.
`legal:approved` and `legal:blocked` make the disposition machine-readable and
allow the orchestrator to fail closed for legally routed changes.

### ADR-002: Preserve conditional routing

Legal review remains conditional so routine low-risk changes do not require a
legal stage. When a qualifying risk is identified, policy and workflow require
the stage before review or deployment can proceed.

### ADR-003: Keep counsel authority outside the workflow

GitHub labels are evidence of the SDLC decision, not legal advice or a
substitute for qualified counsel. The Legal Risk Assessment must record the
evidence and any required human counsel disposition before `legal:approved` is
applied.