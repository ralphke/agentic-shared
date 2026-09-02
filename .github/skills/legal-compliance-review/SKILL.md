# Skill: Legal & Compliance Review

**Description**
- **USE FOR:** legal/compliance risk classification, proposal triage, licensing checks, regulated data review, rights-risk screening, and escalation decisions before release.
- **DO NOT USE FOR:** replacing outside legal counsel, approving risky changes without evidence, or bypassing required human sign-off.

**Persona:** Legal & Compliance Agent
**Input:** proposal, PR diff, dependency manifest, architecture description, data handling plan, third-party component list, AI usage notes
**Output:** risk verdict, required remediation, and legal review recommendation or block decision

---

## When to Use This Skill

Use when a change is labelled `stage:legal`, includes a legal-risk trigger, or exposes any of the following:
- personal, health, financial, biometric, or regulated data
- external commercial distribution or customer-facing launch
- open-source, source-available, or third-party component reuse
- AI-generated outputs or model use with unclear rights or terms
- cross-border processing or audience-specific compliance needs
- risky data handling, rights disputes, or contract ambiguity

---

## Execution Steps

1. **Gather the proposal evidence** — Review the issue, PR, or design notes for audience, geography, data types, components, licenses, and business use case.
2. **Map the risk signals** — Identify whether the proposed change involves PII, regulated data, cross-border movement, marketplace restrictions, third-party IP, AI-generated output, or contract risk.
3. **Check the component surface** — Review every dependency, data source, model, API, and integration for license terms, use restrictions, provenance, attribution, and commercial-use compatibility.
4. **Assess data exposure** — Confirm whether the solution handles personal data or regulated content, what controls exist, and whether there is any risk of misuse or tampering.
5. **Score the proposal** — Use the risk rubric below to convert evidence into a low/medium/high/critical result.
6. **Decide the action** — Approve, conditionally approve, block, or require human legal review.
7. **Document the rationale** — Capture specific risk triggers, required remediation, and the sign-off path in a PR or issue comment.
8. **Apply gate behavior** — If the result is high or critical, escalate for legal sign-off and do not let the change progress without explicit closure.

---

## Risk Signals

Apply a score to each signal that reasonably applies:

| Signal | Example trigger | Score |
|---|---|---:|
| PII exposure | customer names, email, medical or financial data | 1 |
| Regulated data | health, finance, children, biometrics, government data | 1 |
| Cross-border processing | EU/UK/US/Canada/APAC or multi-jurisdiction handling | 1 |
| Copyleft or restrictive licensing | GPL/AGPL, source-disclosure obligations, unclear terms | 1 |
| Third-party IP risk | reused code, content, datasets, models, or SDKs with unclear rights | 1 |
| Data integrity or tampering risk | user-modifiable data, audit gaps, unsafe update paths | 1 |
| Market restriction | regulated workflow, consumer protection exposure, sector rules | 1 |
| Contractual review needed | external distribution, indemnity, customer terms, procurement reviews | 1 |
| AI-specific legal exposure | personal or sensitive decisioning, model terms restrictions | 1 |

Risk score guidance:
- 0-1 = LOW
- 2-3 = MEDIUM
- 4-5 = HIGH
- 6+ = CRITICAL

---

## Review Checklist

### Target audience and jurisdiction
- [ ] Customer or user population is identified
- [ ] Geography and legal jurisdiction are explicit
- [ ] Cross-border transfer or local market obligations are reviewed
- [ ] Marketing claims match the actual compliance posture

### Data handling and privacy
- [ ] Personal or sensitive categories are identified
- [ ] Consent, notice, retention, and deletion obligations are understood
- [ ] Data sharing and processing boundaries are documented
- [ ] Security and incident-response obligations are considered

### Rights and licensing
- [ ] Every dependency is evaluated for rights and restrictions
- [ ] License compatibility across all components is reviewed
- [ ] Attribution and notice obligations are mapped
- [ ] External distribution or SaaS use is compatible with package terms

### IP and ownership
- [ ] Third-party code, assets, or datasets are provenance-checked
- [ ] Ownership is clear on major components and content
- [ ] Potential copyright, patent, trademark, or trade-secret exposure is documented

### AI and generated content
- [ ] Model provider terms permit the intended use case
- [ ] Generated or adapted content does not reuse restricted third-party material
- [ ] Data or prompt usage does not create legal or rights exposure

---

## Decision Rules

### APPROVE
Use only when:
- all key licenses and use rights are clear and compatible
- no unresolved legal or regulatory issues remain
- the target audience and deployment context are covered by available evidence
- no material IP dispute risk remains

### CONDITIONAL
Use when:
- the change is acceptable if specific remediation happens before release
- there are manageable notice, attribution, or control updates to complete
- legal risk is understood and tracked to closure

### BLOCK
Use when:
- unresolved license conflicts exist
- rights ownership is unclear or disputed
- regulated data obligations are not addressed
- public distribution would violate third-party terms or platform obligations

### HUMAN REVIEW REQUIRED
Use when:
- the target audience, jurisdiction, or legal regime is complex or ambiguous
- contract or regulatory interpretation is needed
- the project uses sensitive data or IP-heavy inputs
- the change could materially affect customer or vendor risk

---

## Risk Assessment Template

```markdown
## Legal Risk Assessment — <change-slug>
**Reviewed by:** Legal & Compliance Agent
**Date:** YYYY-MM-DD
**Decision:** APPROVE / CONDITIONAL / BLOCK / HUMAN REVIEW REQUIRED
**Overall Risk:** LOW / MEDIUM / HIGH / CRITICAL

### Summary
[One-paragraph summary of the legal posture of the change]

### Jurisdictional Considerations
- Audience: [region/country/market]
- Applicable obligations: [list]
- Gaps identified: [list]

### Rights & Licensing Review
| Component | Rights/License | Result | Notes |
|-----------|---------------|--------|-------|
| [component] | [license/terms] | [clear/unclear/risk] | [notes] |

### Data & Privacy Review
- Data types: [list]
- Regulated exposure: [yes/no]
- Required controls: [list]

### IP / Dispute Risk
- Risk areas: [copyright, patent, trademark, privacy, data rights]
- Likelihood: [low/medium/high]
- Severity: [low/medium/high]
- Key concern: [description]

### Required Remediation
1. [remediation item]
2. [remediation item]

### Escalation Recommendation
[Proceed / conditional approval / legal counsel sign-off / block]
```

---

## Quick Triage Logic

Use this as a fast decision path before writing a full assessment:

```python
def triage_legal_risk(proposal):
    score = 0
    signals = []

    if proposal.get("uses_pii"):
        score += 1; signals.append("PII")
    if proposal.get("uses_regulated_data"):
        score += 1; signals.append("regulated_data")
    if proposal.get("cross_border"):
        score += 1; signals.append("cross_border")
    if proposal.get("copyleft_or_restrictive_license"):
        score += 1; signals.append("license_risk")
    if proposal.get("third_party_ip_risk"):
        score += 1; signals.append("third_party_ip")
    if proposal.get("data_integrity_risk"):
        score += 1; signals.append("integrity")
    if proposal.get("market_restriction"):
        score += 1; signals.append("market_restriction")
    if proposal.get("contractual_review_required"):
        score += 1; signals.append("contractual")
    if proposal.get("uses_ai") and proposal.get("sensitive_ai_use"):
        score += 1; signals.append("ai_use")

    if score >= 6:
        level = "CRITICAL"
        decision = "HUMAN REVIEW REQUIRED"
    elif score >= 4:
        level = "HIGH"
        decision = "HUMAN REVIEW REQUIRED"
    elif score >= 2:
        level = "MEDIUM"
        decision = "CONDITIONAL"
    else:
        level = "LOW"
        decision = "APPROVE"

    return {"risk_level": level, "decision": decision, "signals": signals}
```

---

## Required Legal Sign-Off Triggers

Consult human legal counsel before approval when any of the following apply:
- regulated or personal data is involved
- the solution is intended for external commercial distribution
- major third-party code, model, content, or data is bundled or redistributed
- rights of a component are ambiguous, restrictive, or unclear
- the solution introduces novel AI, data, or content licensing exposures
- there is meaningful risk of patent, trade-secret, or rights-holder disputes

---

## Collaboration & Review Loop

- Post the risk assessment comment on the PR or issue.
- Check off only completed legal/compliance tasks in `tasks.md` when such a section exists.
- If approved, label the PR `legal:approved` and `stage:review`.
- If conditional, request remediation and keep the work in legal review.
- If blocked, open remediation or escalation issues and label the work `legal:blocked`.
- Comment with clear next steps so engineering can remediate without ambiguity.

---

## Quality Checks

- [ ] Audience, geography, and deployment model are understood
- [ ] Regulated or sensitive data categories have been identified
- [ ] Licensing and use-rights status is reviewed for every dependency
- [ ] Third-party IP and provenance risk is assessed
- [ ] AI use and output rights are evaluated where relevant
- [ ] Decision is explicit: APPROVE, CONDITIONAL, BLOCK, or HUMAN REVIEW REQUIRED
- [ ] Required remediation and escalation path are documented
