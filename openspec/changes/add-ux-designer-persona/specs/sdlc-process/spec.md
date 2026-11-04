# Delta for sdlc-process

## MODIFIED Requirements

### Requirement: Ordered Agent Handoffs

Each agent stage MUST complete before the next begins, signalled by PR labels.
The UX Designer stage follows proposal and precedes architecture; the Architect
MUST receive the UX brief before beginning design. Legal review is a conditional
gate after security review and before code review. A change with legal-risk
triggers MUST receive `stage:legal`; it may advance to `stage:review` only after
a `legal:approved` disposition is present. A change labelled `legal:blocked`
MUST NOT advance to code review or deployment.

| Stage Label       | Responsible Persona | Next Stage                      |
| ----------------- | ------------------- | ------------------------------- |
| `stage:proposal`  | Product Owner       | `stage:ux`                      |
| `stage:ux`        | UX Designer         | `stage:design`                  |
| `stage:design`    | Architect           | `stage:implement`               |
| `stage:implement` | Developer           | `stage:test`                    |
| `stage:test`      | QA Engineer         | `stage:security`                |
| `stage:security`  | Security Engineer   | `stage:legal` or `stage:review` |
| `stage:legal`     | Legal & Compliance  | `stage:review`                  |
| `stage:review`    | Code Reviewer       | `stage:deploy`                  |
| `stage:deploy`    | DevOps/SRE          | `stage:operate`                 |
| `stage:operate`   | Operations SRE      | `archived`                      |

#### Scenario: Proposal hands off to UX before architecture

- GIVEN a proposal accepted for architecture work
- WHEN the Product Owner completes the proposal stage
- THEN the work is routed to `stage:ux`
- AND the Architect does not begin until the UX Designer has produced the UX
  brief
- AND the UX Designer hands the brief to the Architect at `stage:design`

#### Scenario: Missing UX brief blocks architecture

- GIVEN a pull request labelled `stage:design` without a UX brief
- WHEN the design-stage gate validates its required artifacts
- THEN the gate blocks the Architect handoff and reports the missing UX brief

#### Scenario: Stage label gates merge

- GIVEN a PR without the `stage:review` label
- WHEN a merge is attempted
- THEN the merge is blocked by a branch protection rule
- AND a comment lists the incomplete stages

#### Scenario: UX criteria and security gate remain in downstream order

- GIVEN implementation includes UX acceptance criteria from the UX brief
- WHEN the change advances through testing and security
- THEN QA validates the UX criteria, including applicable responsive, keyboard,
  and touch behavior
- AND the change cannot reach review or deployment until its security gate passes

#### Scenario: Legal stage is required for high-risk work

- GIVEN a change identified as having legal-risk triggers
- WHEN it completes security review
- THEN it is routed to `stage:legal` before code review
- AND `stage:review` is rejected until `legal:approved` is recorded

#### Scenario: Legal block prevents deployment

- GIVEN a pull request labelled `legal:blocked`
- WHEN `stage:deploy` is applied
- THEN the SDLC orchestrator fails the deployment gate
- AND the pull request remains blocked pending remediation or counsel sign-off
