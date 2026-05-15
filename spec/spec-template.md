# Spec Template

Use this template for any feature, fix, or change you plan to delegate to an AI coding agent. Fill in all four sections before writing a single line of code or submitting an issue.

---

## Proposal

> What are we changing and why?

One paragraph. State the problem, the proposed solution, and the expected benefit. Be specific enough that someone who hasn't seen the codebase can understand the intent.

**Example:**
> The login page currently accepts any non-empty string as a password, leading to accounts with trivially weak credentials. We will add server-side password strength validation that rejects passwords shorter than 8 characters or without at least one non-alphabetic character. This reduces account compromise risk and aligns with our security policy.

---

## Requirements / Scenarios

> How should it behave? Write scenarios in Given/When/Then format.

Each scenario becomes a test case. Be exhaustive at the boundaries.

```
Scenario: [short name]
  Given [precondition]
  When  [action]
  Then  [expected outcome]
```

**Minimum: 3 scenarios. Include at least one unhappy path.**

| # | Scenario | Given | When | Then |
|---|----------|-------|------|------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

---

## Design

> How will it be built?

- **Function / API signature:**
- **Inputs and types:**
- **Outputs and types:**
- **Error handling:**
- **Dependencies / libraries:**
- **Constraints** (performance, security, backwards-compatibility):

For UI changes: include a sketch or describe the layout change.  
For API changes: include request/response schemas.

---

## Tasks

> What needs to be done, in order?

Number every step. The agent will use this list to drive implementation.

1. [ ] 
2. [ ] 
3. [ ] 
4. [ ] 

---

## Out of scope

List anything explicitly excluded so the agent does not over-build.

- 
- 

---

## Acceptance criteria

One-sentence, verifiable statements. All must be true before the change is merged.

- [ ] 
- [ ] 
- [ ] 
