# Tasks

## 1. Retire Shared Entry Points and Guidance

- [x] 1.1 Remove the 13 shared root-level `.prompt.md` wrappers and verify
      their maintained skill counterparts remain available while no shared
      wrappers remain.
- [x] 1.2 Update README, shared Copilot guidance, and OpenSpec workflow
      instructions to describe skills as the shared entry points; verify
      current guidance no longer promises prompt-wrapper compatibility and
      still documents consumer-local prompts.

## 2. Update Enforcement and Synchronization Tests

- [x] 2.1 Remove wrapper targets from policy restoration and update its tests;
      verify policy restoration succeeds using maintained skill files only.
- [x] 2.2 Remove tests that read or require deprecated prompt wrappers while
      preserving OpenSpec CLI and skills-only workflow checks; run the
      affected command-skill and strict-policy tests.
- [x] 2.3 Add a synchronization regression test that removes an unchanged
      installed shared prompt wrapper and preserves a protected local prompt;
      run the focused synchronization tests.

## 3. Verify the Complete Change

- [x] 3.1 Run strict OpenSpec validation for `retire-shared-prompts` and the
      focused tests from the preceding tasks; confirm the delta, documentation,
      restoration script, and sync behavior agree with the proposal.
