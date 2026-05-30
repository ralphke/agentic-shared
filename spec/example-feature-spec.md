# Example Spec: Email Address Validation

This is a filled-in example following `spec-template.md`. Use it as a reference when writing your own specs.

---

## Proposal

The registration form currently accepts any string in the email field, causing invalid addresses to reach the database and generate bounce errors on transactional mail. We will add a `validateEmail` utility function that checks whether a string is a well-formed email address. The function will be used by the registration and profile-update forms to gate submission.

---

## Requirements / Scenarios

```
Scenario: Valid standard email is accepted
  Given the string "alice@example.com"
  When  validateEmail is called
  Then  it returns true

Scenario: Missing @ symbol is rejected
  Given the string "aliceexample.com"
  When  validateEmail is called
  Then  it returns false

Scenario: Missing domain is rejected
  Given the string "alice@"
  When  validateEmail is called
  Then  it returns false

Scenario: Missing local part is rejected
  Given the string "@example.com"
  When  validateEmail is called
  Then  it returns false

Scenario: Empty string is rejected
  Given an empty string ""
  When  validateEmail is called
  Then  it returns false

Scenario: Subdomain email is accepted
  Given the string "alice@mail.example.co.uk"
  When  validateEmail is called
  Then  it returns true

Scenario: Leading/trailing whitespace is rejected
  Given the string "  alice@example.com  "
  When  validateEmail is called
  Then  it returns false
```

---

## Design

- **Function signature:** `validateEmail(value: string): boolean`
- **Input:** any string value from a form field
- **Output:** `true` if well-formed, `false` otherwise
- **Error handling:** must not throw; always returns a boolean
- **Dependencies:** no third-party libraries — use a regex that covers RFC 5321 common cases
- **Constraints:** must run in both browser and Node.js environments; no async

**Regex to use (conservative, covers 99 % of real-world addresses):**
```
/^[^\s@]+@[^\s@]+\.[^\s@]+$/
```

---

## Tasks

1. [x] Create `src/utils/validateEmail.ts` with the `validateEmail` function
2. [x] Export `validateEmail` from `src/utils/index.ts`
3. [x] Write unit tests in `test/utils/validateEmail.test.ts` covering all 7 scenarios above
4. [ ] Wire into registration form: gate submit button when `validateEmail` returns false
5. [ ] Wire into profile-update form: same gate logic

---

## Out of scope

- Full RFC 5321 compliance (quoted strings, IP address literals)
- DNS MX record lookup
- Internationalized domain names (IDN)

---

## Acceptance criteria

- [ ] `validateEmail` returns `true` for all valid scenarios listed above
- [ ] `validateEmail` returns `false` for all invalid scenarios listed above
- [ ] Function does not throw on any string input
- [ ] All unit tests pass in CI
