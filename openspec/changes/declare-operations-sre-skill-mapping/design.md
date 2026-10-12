# Design

## Context

See `proposal.md` for the motivation and `specs/personas/spec.md` for the behavior contract. The Operations SRE Agent currently names its responsibilities and archive trigger, while the shared skill files separately describe their purpose and triggers.

## Goals / Non-Goals

**Goals:**
- Make the agent's intended skill associations and use conditions clear at the point where the agent's instructions are read.
- Keep the mapping consistent with the existing operational gates and skill descriptions.

**Non-Goals:**
- Add runtime skill-routing or exclusivity behavior.
- Change skill discovery, skill contents, or another agent definition.

## Decisions

### Declare associations in the agent instructions

Add an `Associated Skills` section to `.github/agents/operations-sre.agent.md` and name each skill by its existing directory/name. For each skill, provide a brief use condition and link it to the relevant agent responsibility.

The agent file is the clearest point-of-use location. The skills do not have a shared machine-readable ownership field, and adding an unsupported `skills:` frontmatter key could be ignored by the runtime. A separate overview table would duplicate the mapping without guiding the agent directly.

### Treat the mapping as guidance, not access control

The section SHALL describe intended use only. Skill discovery and invocation remain governed by the runtime and the skill descriptions; no claim of exclusive assignment or enforcement is made.

### Preserve operational gates for archive use

The `openspec-archive-change` association SHALL be conditional on the Operations SRE Agent's existing archive criteria. It must not bypass those checks or replace the archive skill's own workflow.

## Risks / Trade-offs

- **The runtime may not prioritize a named skill solely because it appears in the agent body** → State the skill names and triggers explicitly, while avoiding claims of automatic or exclusive routing.
- **The mapping could drift if a skill is renamed or its purpose changes** → Refer to the canonical skill slug and keep the use condition concise and aligned with its description.

## Migration Plan

Update the shared agent definition, validate the changed asset, and distribute it to consumers through the existing versioned shared-assets synchronization process. No consumer-side override or runtime migration is required.
