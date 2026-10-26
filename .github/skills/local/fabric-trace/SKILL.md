---
name: fabric-trace
description: Opt in to a revision-bound Software Fabric execution trace. Use when asked to trace a Software Fabric change, record a Fabric execution trace, run OpenSpec apply with tracing, or check a Fabric trace. Do not use for ordinary apply requests unless tracing is requested.
license: MIT
---

# Fabric Execution Trace

## Purpose and limits

Use the local trace CLI to record observable activity and evaluate revision-bound
evidence for one OpenSpec change. This is an opt-in wrapper; it does not dispatch
personas, capture all host activity, or make an ordinary apply run the complete
Software Fabric. Read the [trace guide](../../../../doc/fabric-execution-trace.md)
and the [SDLC instructions](../../../../.github/instructions/sdlc-fabric.instructions.md)
before starting. Keep the approved change scope and preserve unrelated worktree
changes.

## Workflow

1. Identify the exact OpenSpec change and repository. Do not guess a change
   directory from a slug. For a new trace, initialize against the explicit
   change directory:

   ```powershell
   python scripts/fabric_trace.py init `
     --repo . `
     --change-dir openspec/changes/<change>
   ```

   Capture the printed `.fabric-traces/<traceId>` path as `$traceDir`. Resume an
   existing trace only when its repository, change directory, and target
   revision are still the intended ones. If the implementation revision
   changed, initialize a new trace and link the prior trace with
   `--predecessor <traceId>`; do not carry gate success forward.

2. Record that the local tracing skill and applicable instructions were
   included. Manual activity remains self-reported and cannot satisfy a gate:

   ```powershell
   python scripts/fabric_trace.py record `
     --trace-dir $traceDir `
     --kind skill_load `
     --stage implement `
     --summary "Loaded the local fabric-trace skill"
   python scripts/fabric_trace.py record `
     --trace-dir $traceDir `
     --kind instruction_inclusion `
     --stage implement `
     --summary "Read the Software Fabric instructions"
   ```

3. Explicitly invoke the existing
   [`openspec-apply-change` skill](../../openspec-apply-change/SKILL.md) for the
   selected change. In Copilot chat, use the `openspec-apply-change` skill or
   `/openspec-apply-change <change>`. Keep its OpenSpec store selection and task
   order; do not replace it with an untraced implementation or a deprecated
   prompt wrapper. The wrapper records that apply was requested, not that every
   persona ran.

4. Execute the relevant validation through `run`, using an appropriate stage
   and the repository's actual test command. The child command follows `--`:

   ```powershell
   python scripts/fabric_trace.py run `
     --trace-dir $traceDir `
     --stage test `
     --summary "Run focused tests" `
     -- python -m unittest discover -s tests -p "test_fabric_trace*.py"
   ```

   A nonzero child exit is recorded and returned. Do not treat a successful
   process exit alone as structured test evidence or coverage proof.

5. If an authorized pull request is available, optionally collect provider
   observations with the read-only GitHub collector. Check the configured
   account first; if access is unavailable, report that limitation and do not
   substitute cached evidence or attempt a write operation:

   ```powershell
   gh auth status --hostname github.com
   python scripts/fabric_trace.py collect-github `
     --trace-dir $traceDir `
     --repo OWNER/REPOSITORY `
     --pr 123
   ```

6. Generate both reports and check readiness:

   ```powershell
   python scripts/fabric_trace.py report --trace-dir $traceDir
   python scripts/fabric_trace.py check --trace-dir $traceDir
   ```

   `report` can successfully render an incomplete trace. `check` returns
   nonzero unless the evaluated result is `verified-complete`; preserve that
   result and its missing or failed evidence as an honest gap, not as a reason
   to bypass a gate.

## Quality checks and guardrails

- Confirm the report names all nine stages, the target revision, policy digest,
  provenance, evidence references, observation boundary, and next evidence.
- Distinguish recorded activity from verified gates. Mark manual claims and
  session references as self-reported; do not infer agent invocation or stage
  completion.
- Respect required security and conditional legal review. Do not merge without
  the security gate, deploy without passing tests and the required coverage,
  or archive without operations/SLO readiness.
- Do not change generic apply skills/prompts, managed instructions, or
  workflows. Do not change labels, post comments, dispatch workflows, approve,
  merge, deploy, or archive through this local tracing flow.
- Keep credentials, raw prompts, source contents, environment values, and
  command output out of trace summaries and metadata.

## Final output

Report the trace directory and target revision, validation commands and their
observed exits, whether optional GitHub collection ran, the report/check status,
verified gates, missing or failed evidence, and the trace's observation
boundary. State explicitly that tracing is opt-in and does not prove
unobserved persona activity or a real deployment. Do not claim
`verified-complete` unless `check` returned success.

## References

- [Trace CLI](../../../../scripts/fabric_trace.py)
- [Trace guide](../../../../doc/fabric-execution-trace.md)
- [Software Fabric instructions](../../../../.github/instructions/sdlc-fabric.instructions.md)
- [OpenSpec apply skill](../../openspec-apply-change/SKILL.md)
