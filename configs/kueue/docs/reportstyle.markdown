# CANFAR architecture report style

This document captures the report-writing preferences inferred from the current
CANFAR Kueue architecture package. It is based on the edited state of
`architecture.md`, `roadmap.md`, `operations.md`, `ui-spec.md`, and the ADR
set.

The goal is not to define a generic technical writing style. The goal is to
capture the specific way these CANFAR architecture and planning reports are
meant to read.

## 1. Core writing motivation

The core motivation behind this report style is clarity for decision-makers,
operators, and technical reviewers.

These reports are not meant to be literary, conversational, or highly abstract.
They are meant to:

- explain a system design clearly
- support architectural review and technical decision-making
- preserve operational intent
- make scope and ownership boundaries obvious
- connect policy, implementation, and future roadmap in one narrative

The writing therefore favors directness, structure, and explicit reasoning over
personality, flourish, or overly soft phrasing.

## 2. High-level style traits

The current edits consistently show the following preferences.

### 2.1 Formal report framing

Document titles are framed as formal report titles, not lightweight notes. For
example:

- `CANFAR Science Platform Kueue Architecture`
- `CANFAR Kueue Roadmap`
- `Architecture Decision Records`

This style treats each document as part of a reviewable architecture package.

### 2.2 Direct, declarative tone

The preferred tone is factual and assertive. Statements are written as design
claims, requirements, or observations. The writing avoids unnecessary hedging
and avoids casual filler.

Preferred pattern:

- "The current repository baseline still reflects an older Kueue deployment."
- "The architecture serves the following groups."
- "This phase focuses on making scheduling behavior understandable to users and
  admins."

Avoid:

- conversational asides
- rhetorical questions
- motivational language
- vague claims without operational meaning

### 2.3 Platform-first wording

The reports should speak about the CANFAR Science Platform as a real operating
environment, not as a generic software project. The preferred writing makes the
platform identity explicit and keeps the narrative centered on actual tenant,
operator, and workload needs.

Preferred pattern:

- "The CANFAR Science Platform needs..."
- "This document is the primary architecture reference for Kueue rollout on the
  CANFAR Science Platform."

## 3. Structural preferences

The current edits show a strong preference for highly structured reports.

### 3.1 Numbered major sections

Use numbered top-level sections and numbered subsections. This makes the reports
 easy to review, annotate, and discuss in meetings.

Preferred pattern:

- `## 1. Introduction`
- `### 1.1 Problem statement`
- `### 1.2 Users and stakeholders`

### 3.2 Title Case section headings

The current edits move headings toward Title Case for important report
subsections.

Preferred pattern:

- `Success Criteria`
- `Quality Goals`
- `Repository and Deployment Baseline`
- `Service Level Indicators (SLIs) and Objectives (SLOs)`

This indicates a preference for a formal report look over sentence-case prose
headings.

### 3.3 Short overview paragraph before lists

Each section begins with a short framing paragraph before bullets or numbered
items. This is important. The reports are not lists with headings attached. They
are structured narratives that then break into lists.

### 3.4 Parallel list structure

Bullets are short, parallel, and information-dense. Lists are used to enumerate
requirements, deliverables, activities, or consequences, not for decorative
formatting.

Preferred pattern:

- "community-owned resources remain a first-class concept"
- "communities can lend and borrow unused capacity"
- "projects compete fairly inside their community"

## 4. Content preferences

The edits reveal several consistent content choices.

### 4.1 Remove repo noise from narrative sections

When discussing the current baseline, the preferred report style summarizes the
state directly instead of embedding too many file-path references inside the
main prose.

Preferred pattern:

- "Current deployment documents `0.11.6` as the installed release"
- "Current deployment uses `batch/job` only"

This keeps the main report readable. File-level evidence can still exist, but
the report itself should read like an architecture document, not a code review.

### 4.2 Keep implementation awareness without dropping into code detail

The preferred style is technically specific, but not source-code heavy. It names
real systems, CRDs, workloads, and policies, but it does not drown the report
in low-level manifest detail unless the detail matters for a decision.

### 4.3 Emphasize scope boundaries

The reports should say clearly what is in scope, what is out of scope, and what
is future work.

Preferred pattern:

- "This service is out of scope for phase 1 implementation, but it is in scope
  for architecture and requirements."
- "Those namespace changes are future roadmap items, not phase 1 requirements."

This is one of the strongest recurring preferences in the edits.

### 4.4 Make ambiguity explicit

The report style does not hide open issues. It records them directly and
operationally.

Preferred pattern:

- "The submission path can resolve project and community deterministically for
  the selected mapping model, or require explicit project selection when the
  mapping model is ambiguous."

This suggests a strong preference for showing the real operational implication of
an open decision rather than just saying that a question remains open.

## 5. Communication style preferences

The communication style is best described as formal, practical, and reviewable.

### 5.1 Write for architects, operators, and reviewers

The reports should read as if they are written for:

- architecture reviewers
- platform operators
- technical leads
- future implementers

They should not read like marketing material or general onboarding content.

### 5.2 Prefer precise nouns over expressive prose

The edits favor terms like:

- baseline
- target state
- future state
- deliverables
- dependencies
- acceptance criteria
- ownership
- scope
- consequences

This reflects a preference for decision and execution vocabulary.

### 5.3 Prefer explicit operational language

When possible, use operationally meaningful wording:

- "rollback"
- "admission collapse"
- "preemption storm"
- "safe operating region"
- "measured thresholds"

This style grounds the report in real system behavior rather than abstract
architecture theory.

## 6. Writing rules to preserve this style

Use these rules when writing future CANFAR architecture reports.

### 6.1 Titles and headings

- Use strong document titles that name the platform and the document purpose.
- Use numbered sections.
- Use Title Case for major subsection headings when the document is formal and
  report-like.

### 6.2 Paragraph style

- Start sections with a short framing paragraph.
- Keep paragraphs compact and high-signal.
- Use direct statements.
- Avoid unnecessary hedging unless uncertainty itself is the point.

### 6.3 Lists

- Use bullets for requirements, traits, risks, and deliverables.
- Use numbered lists for flows, steps, or ordered explanations.
- Keep list items parallel and concise.

### 6.4 Scope and decisions

- State what is current, what is target, and what is future.
- Mark out-of-scope items clearly.
- Record open decisions in a way that shows operational impact.
- Tie every recommendation to either architecture, operations, or roadmap
  intent.

### 6.5 References and evidence

- Keep the main report readable first.
- Use file paths, manifests, and implementation references sparingly in the main
  narrative.
- Prefer summarized statements in the report body and detailed references in
  supporting material.

## 7. Preferred report voice

The best voice for these reports is:

- formal
- technical
- direct
- practical
- audit-friendly
- operator-aware

The voice is not:

- casual
- academic in an abstract sense
- promotional
- speculative without labeling the speculation

## 8. Template for future reports

Use the following pattern for future architecture or roadmap reports:

1. Start with a direct statement of purpose.
2. State the current baseline or current problem plainly.
3. Define the target design or target operating model.
4. Separate current, target, and future state clearly.
5. Use lists for requirements, activities, risks, and acceptance criteria.
6. Keep open decisions visible and explain their impact.
7. End sections with operational implications, not just abstract conclusions.

## 9. Summary

Your report-writing preference is not simply "formal technical writing." It is a
specific style optimized for platform architecture review:

- strong document framing
- direct declarative language
- explicit scope boundaries
- operationally meaningful wording
- high-structure sectioning
- open decisions recorded with consequences
- readable narrative without excessive repo-level clutter

That combination is what gives the package its current voice.
