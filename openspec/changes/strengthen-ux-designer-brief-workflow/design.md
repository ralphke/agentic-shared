# Design

## Context

See `proposal.md` for motivation and
`specs/personas/spec.md` for the observable UX brief contract.

The existing UX persona already owns the `ux-brief.md` handoff, the WCAG
2.2 AA target, responsive expectations, and the boundary with architecture and
QA. The existing persona test checks that these core instructions remain
present. There is no UX-specific skill yet; other stage skills use a repeatable
structure with a trigger, inputs/outputs, execution steps, quality checks, and
error handling.

## Goals / Non-Goals

**Goals:**

- Add a concise, repeatable method for turning accepted requirements into a
  traceable, testable UX brief.
- Make evidence, assumptions, interaction states, accessibility, and
  handoff-quality checks explicit.
- Keep the method proportionate to affected visual surfaces; nonvisual
  changes bypass UX work under the accepted conditional-UX change.

**Non-Goals:**

- Add design tooling, dependencies, application code, or a visual design
  system.
- Require external user research, prototypes, or device testing when evidence
  and environments are not available.
- Move product-scope decisions, technical choices, or QA validation to the UX
  Designer.

## Decisions

1. **Keep the persona as the role contract and the skill as the procedure.**
   The persona will state responsibilities, boundaries, and a direct reference
   to the skill. The skill will hold the detailed workflow and checklist.
   Duplicating the full checklist in both files was rejected because it invites
   drift.
2. **Ground the brief only in available approved evidence.** The skill will
   inspect the accepted proposal, relevant specs, and available constraints.
   It will distinguish those facts from assumptions and open questions. It
   will ask the Product Owner when missing or conflicting information could
   change experience requirements; it will not fabricate research findings.
3. **Use a structured, traceable brief.** The skill will direct the agent to
   record users and goals, scope, journeys, affected visual surfaces,
   applicable interaction states, content, accessibility, responsive behavior
   where applicable, and observable acceptance criteria tied to their source
   needs. The brief will keep open questions and technology-risk flags
   separate from accepted requirements.
4. **Make accessibility specific but conditional.** Preserve WCAG 2.2 AA, then
   specify applicable checks for keyboard and focus, semantics and labels,
   contrast and non-color cues, zoom or reflow, error communication, reduced
   motion, and touch. Mark dimensions not applicable with a reason. Do not
   present a target as proof of conformance.
5. **Preserve nonvisual exemptions and stage ownership.** The accepted
   `conditional-ux-stage-and-validation` change supersedes the earlier
   nonvisual brief rule. CLI/API/framework changes with no affected visual
   interface require no UX artifacts, specs, or tests. Architecture and QA
   retain ordinary functional planning and validation.
6. **Validate the authored contract, not UX quality by string presence alone.**
   Extend focused tests to assert the persona-to-skill reference and required
   skill sections and key constraints. Use Markdown lint and OpenSpec
   validation, and record a lightweight before/after comparison against the
   existing skill/persona quality rubric. Do not add a benchmark framework.

## Risks / Trade-offs

- **A long skill could overwhelm small changes** → Make every checklist
  dimension conditional and require rationale only for material
  non-applicability or unresolved context.
- **Persona and skill guidance could drift** → Keep shared details in the skill
  and the persona reference concise; test the linkage and critical invariants.
- **A WCAG target could be mistaken for verified compliance** → State that
  criteria describe expected behavior and only QA evidence may claim testing.
- **Sparse proposal evidence could block a brief** → Ask targeted questions
  only when unknowns materially affect experience requirements; record
  non-blocking assumptions explicitly.

## Migration Plan

1. Add the UX design skill and update the UX persona to direct the agent to it.
2. Add focused tests and a short baseline-versus-improved quality assessment.
3. Run focused tests, Markdown lint, and strict OpenSpec validation.

No consumer migration or rollback procedure is required; reverting the skill,
persona reference, and focused tests restores the prior behavior.
