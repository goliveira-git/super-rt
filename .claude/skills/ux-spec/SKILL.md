---
name: ux-spec
description: Format and quality bar for UX specs — flows, layout, every component state, interaction detail, microcopy, and the accessibility checklist. Use when writing a spec, and when building UI from one to know what it obligates.
---

# UX spec

Creative guidance. A spec is done when someone can build the whole feature from it without inventing an interaction or asking what happens on error.

Specs live in `docs/ux/<feature>.md`. Specify **behavior and structure**, never framework APIs — a spec should survive a change of stack.

## Spec format

### 1. Purpose
What the user is trying to accomplish and what success means to *them*. One paragraph. If you cannot write this, you do not yet understand the feature.

### 2. Users and context
Who is doing this, how often, what they know, and what device and conditions they're in. Design for the user described at kickoff.

### 3. Flow
Entry points → each step → decision points → exits. Include what happens when someone abandons partway, arrives with stale data, or uses the back button. Cover the paths people actually take, not just the demo path.

### 4. Layout
For each screen: what is present, what dominates, what is secondary, and the reading order. How it reflows at narrow widths — mobile is a first-class layout, not a degraded one. Structure over pixels: "primary action bottom-right, always visible without scrolling" is more useful than a measurement.

### 5. States
Specify **every** one that applies. Most interfaces fail here, so design these before the happy path:

- **Loading** — first load vs. refresh; skeleton, spinner, or optimistic content; what the user can do meanwhile.
- **Empty** — never a blank region. What it says, and the one action that fills it.
- **Partial** — some data present, some missing or still arriving.
- **Error** — per failure type: validation, not found, permission denied, network, server, timeout. What it says, what the user can do, what is recoverable.
- **Success** — what confirms it, how long it persists, what changes on screen.
- **Disabled / read-only** — why, and whether the user is told why.

### 6. Interaction detail
What is interactive, what happens on activation, transitions and their purpose, optimistic updates and their rollback, confirmation for destructive actions, and what cannot be undone. Name the undo path or state plainly that there isn't one.

### 7. Content
Real microcopy — labels, buttons, helper text, empty states, every error message. Write the actual words.

Error messages say what happened, why, and what to do next. "An error occurred" is an unfinished design. Buttons are verbs describing the outcome: "Save changes", not "OK" or "Submit".

### 8. Accessibility requirements
Written as build requirements, so they are treated as part of the task:

- **Keyboard** — the full path through the flow using only a keyboard. Tab order, what each key does, how to escape or cancel.
- **Focus** — where focus starts, where it moves after an action, how it's trapped in a modal and restored on close. Visible focus indicator everywhere.
- **Semantics** — the correct element for each role: real buttons, real links, real headings in order, real lists, real labels bound to inputs. ARIA only when no semantic element does the job.
- **Dynamic content** — what gets announced when it changes, and how urgently.
- **Contrast** — target ratio (default WCAG AA: 4.5:1 body, 3:1 large text and UI boundaries). Never use color as the only carrier of meaning.
- **Motion** — what is reduced or removed under a reduced-motion preference.
- **Targets** — minimum hit area for anything touchable.
- **Images and icons** — alt text for meaningful ones, hidden from assistive tech when decorative.

### 9. Open questions
What you could not resolve and who must resolve it. Better in the spec than discovered mid-build.

## Design principles

- **Remove steps before adding features.** The best interaction is often the one you deleted.
- **Design the error and empty states first.** They reveal what the feature really is.
- **Make the decision.** Don't leave three options open — that just defers the design work to build time.
- **Respect what the user already typed.** Never silently discard input on a failure.
- **Destructive actions need friction, everything else needs none.**

## When building from a spec

Sections 5, 6, and 8 are obligations, not suggestions: every listed state must be implemented, and the accessibility requirements ship with the feature rather than after it. Implementing only the happy path is an incomplete task, not a first draft.

If a spec detail is impossible or wrong, say so and propose an alternative — deviating is allowed, deviating silently is not.

## Related plugin skills

Invoke these when the situation matches; this skill still sets the bar.

- `frontend-design:frontend-design` — for aesthetic direction, typography, and visual choices the spec leaves open.
- `dataviz` — before specifying any chart, graph, or dashboard.
