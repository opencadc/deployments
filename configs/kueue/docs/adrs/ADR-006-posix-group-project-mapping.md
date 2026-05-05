# ADR-006: POSIX group to project mapping options

- Status: Proposed
- Date: March 12, 2026

## Context

Projects may contain multiple POSIX groups and communities may contain multiple
projects. The open question is whether a POSIX group may belong to more than one
project.

This decision changes the submission experience because ambiguous group mapping
may force the API layer to require an explicit project field.

## Options

### Option A: One group maps to exactly one project

Under this option, a POSIX group may not belong to multiple projects.

#### Benefits

- `Skaha` can often infer project and community from group context
- submission stays simpler for users
- visibility and accounting reasoning stay easier to explain

#### Costs

- the identity model is stricter
- some administrative use cases may need new group structures

### Option B: A group may map to multiple projects

Under this option, a POSIX group may belong to more than one project.

#### Benefits

- the identity model is more flexible
- administrators can reuse groups across projects

#### Costs

- the submission path must require explicit project selection in ambiguous cases
- user experience becomes more complex
- the control service and UI must explain ambiguity clearly

## Current direction

Leave the decision open. The architecture and UI must support both models until
the tenant administration workflow is finalized.
