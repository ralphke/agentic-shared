# OpenSpec Changes Directory

This directory contains **in-flight changes** — proposed modifications to the
Software Fabric.

Each change gets its own folder containing OpenSPEC artifacts:

```text
changes/
├── <change-slug>/          ← One folder per in-flight change
│   ├── proposal.md         ← Intent, scope, acceptance criteria (Product Owner)
│   ├── design.md           ← Technical approach, ADRs, diagrams (Architect)
│   ├── tasks.md            ← Numbered implementation checklist (Architect)
│   └── specs/              ← Delta specs (ADDED / MODIFIED / REMOVED)
│       └── <domain>/
│           └── spec.md
└── archive/                ← Completed changes (merged into specs/)
    └── YYYY-MM-DD-<slug>/
```

## Lifecycle

```text
/openspec-propose <slug>  →  changes/<slug>/ created
/openspec-apply           →  tasks implemented, PR opened
/openspec-sync            →  delta specs merged into specs/ (preview)
/openspec-archive         →  changes/<slug>/ moved to changes/archive/
```

## Creating a New Change

Using VS Code Copilot:

```text
/openspec-propose <your-idea-slug>
```

Or copy the idea template:

```bash
cp openspec/templates/idea-to-spec.md openspec/changes/<slug>/proposal.md
```

See `openspec/config.yaml` for project-level settings. See `openspec/specs/` for
the current source-of-truth specs.
