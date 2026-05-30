# Operations — Source of Truth

> **Domain:** `operations` | **Owner:** devops-sre  
> Defines deployment patterns, observability standards, SLO requirements,
> runbook conventions, and incident response for the Software Fabric.

---

## Overview

The Operations domain covers everything after code is merged: how applications
are deployed, monitored, and maintained in production. The DevOps/SRE and
Operations SRE agents share responsibility for this domain.

---

## Requirements

### Requirement: Staged Deployment Pipeline
Every change MUST be deployed through a staged pipeline before reaching production.

**Pipeline stages:**
```
PR Merge → Build → Unit Tests → Container Build
        → Deploy Dev → Smoke Tests
        → Deploy Staging → Integration Tests + Performance Baseline
        → Manual Gate (P0/P1) or Auto-approve (P2/P3)
        → Deploy Production → Smoke Tests → SLO Monitor
```

#### Scenario: Successful staged deployment
- GIVEN a merged PR that passes all CI gates
- WHEN the deployment pipeline triggers
- THEN the change is deployed to dev, then staging (with tests at each stage)
- AND IF all staging tests pass, production deployment proceeds automatically for P2/P3
- AND a deployment summary is posted to the PR and Slack/Teams channel

#### Scenario: Staging failure triggers rollback
- GIVEN a staging deployment where integration tests fail
- WHEN the deployment pipeline detects the failure
- THEN staging is automatically rolled back to the previous stable version
- AND an incident issue is opened with `deploy-failed` label
- AND production is NOT affected

---

### Requirement: Health Checks
Every deployed service MUST expose a health check endpoint.

**Health check specification:**
- `GET /health` — liveness probe: returns 200 if process is alive
- `GET /health/ready` — readiness probe: returns 200 only when ready to serve traffic
- `GET /health/startup` — startup probe: returns 200 only after full initialization
- Response body MUST include: `{"status": "ok", "version": "<semver>", "timestamp": "<ISO8601>"}`

#### Scenario: Health check enables zero-downtime deployment
- GIVEN a Kubernetes rolling deployment
- WHEN a new pod starts
- THEN traffic is only routed to the pod AFTER `/health/ready` returns 200
- AND the old pod continues serving traffic until the new pod is ready

---

### Requirement: Observability — Metrics, Logs, Traces
Every production service MUST emit the three observability pillars.

**Metrics (via Prometheus/Azure Monitor):**
- Request rate (req/s), error rate (%), latency (p50/p95/p99)
- Custom business metrics for key user actions
- Resource utilization (CPU, memory, disk)

**Logs (structured JSON):**
- All log entries MUST include: `timestamp`, `level`, `service`, `traceId`, `message`
- Log levels: ERROR for exceptions, WARN for degraded states, INFO for key events
- No PII (personally identifiable information) in log output
- Log retention: 30 days hot, 1 year cold

**Traces (OpenTelemetry):**
- Distributed traces for all inter-service calls
- Trace sampling: 100% for errors, 10% for normal traffic
- Trace propagation via `W3C TraceContext` headers

#### Scenario: New endpoint is observable from day one
- GIVEN a new API endpoint deployed to production
- WHEN a request is made to the endpoint
- THEN the request appears in: metrics dashboard, structured logs, and distributed trace
- AND the trace spans from the load balancer through all downstream services

---

### Requirement: Service Level Objectives (SLOs)
Every user-facing service MUST have defined and monitored SLOs.

**Minimum SLO set per service:**
| SLO                | Default Target  | Measurement Window |
|--------------------|-----------------|-------------------|
| Availability       | 99.9% (3 nines) | Rolling 30 days   |
| Latency p99        | < 500ms         | Rolling 7 days    |
| Error Rate         | < 0.1%          | Rolling 24 hours  |
| Deployment Success | > 95%           | Per quarter       |

**SLO process:**
1. Operations Agent defines SLOs in `spec/openspec/specs/operations/slo-register.md`
2. Alerts fire when SLO burn rate exceeds threshold (multi-window alerting)
3. SLO violations trigger incident response workflow

#### Scenario: SLO breach triggers alert
- GIVEN a service whose error rate rises above 0.1% for > 5 minutes
- WHEN the SLO monitoring system detects the breach
- THEN a P1 alert fires to the on-call engineer
- AND an incident issue is automatically opened in GitHub
- AND the alert links to the relevant dashboard and runbook

---

### Requirement: Runbooks
Every operational scenario MUST have a runbook before going to production.

**Runbook format:**
- Location: `doc/runbooks/<service>/<scenario>.md`
- Sections: Summary, Detection, Diagnosis Steps, Resolution Steps, Escalation, Post-Mortem
- Linked from: monitoring alerts, incident issues, and the service's README

#### Scenario: Runbook reduces MTTR
- GIVEN an on-call engineer receives an alert at 3am
- WHEN they open the alert
- THEN the alert description links directly to the relevant runbook
- AND the runbook provides step-by-step diagnosis and resolution instructions
- AND the runbook was last reviewed within 90 days

---

### Requirement: Incident Response
Production incidents MUST follow a defined response process.

**Severity levels:**
| Severity | Definition                          | Response Time | Escalation   |
|----------|-------------------------------------|---------------|--------------|
| SEV-1    | Complete service outage             | 5 minutes     | Auto-escalate|
| SEV-2    | Major feature unavailable           | 15 minutes    | PD/Teams     |
| SEV-3    | Degraded performance                | 1 hour        | Next business |
| SEV-4    | Minor issue, workaround available   | Next sprint   | Backlog      |

#### Scenario: SEV-1 incident triggers automatic response
- GIVEN availability drops below 99% for > 2 minutes
- WHEN the SEV-1 alert fires
- THEN an incident issue is opened with `sev-1` label
- AND the on-call engineer is paged via PagerDuty/Teams
- AND the Operations Agent begins automated diagnosis
- AND a status page entry is created

---

### Requirement: Infrastructure as Code
All infrastructure MUST be defined as code and version-controlled.

**IaC requirements:**
- Use Bicep (Azure), Terraform, or Docker Compose as appropriate
- IaC files MUST be stored under `infrastructure/` in the repository
- Every infrastructure change follows the same OpenSPEC change process
- IaC plans are reviewed before apply (PR-based workflow)
- State files MUST be stored in a remote backend (Azure Blob Storage, Terraform Cloud)
