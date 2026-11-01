# UI/UX design gate

## Precedence

Apply this order:

1. Existing design system, repository constraints, and proven product patterns
2. Accepted product requirements and user journeys
3. Two or three explicit design directions for new or substantially reworked surfaces
4. UI/UX catalog recommendations
5. Component-library implementation guidance
6. Browser, accessibility, responsive, and interaction evidence

A generated catalog result is evidence to consider, not authority. Do not replace established tokens, typography, spacing, icons, or interaction language because a generic recommendation differs.

## Route specialists

Use an installed UI/UX research skill to explore patterns, accessibility heuristics, typography, color, interaction, and stack advice. Use the repository's component specialist (for example shadcn) for implementation. Use browser-verification skills for visual evidence.

## New surface or redesign

Before code, present 2–3 genuinely distinct directions. For each, state information hierarchy, interaction model, visual character, accessibility implications, implementation cost, and consistency with the existing product. Recommend one and obtain approval.

Create a compact design contract: tokens reused/added, component states, responsive behavior, content hierarchy, keyboard/focus behavior, loading/empty/error states, and acceptance screenshots or references.

## Small correction

For a localized visual bug or obvious consistency fix, skip direction exploration. Identify the existing precedent, implement the smallest consistent correction, and verify it.

## Browser evidence

Verify the complete journey, not only a component render:

- relevant desktop and mobile widths;
- keyboard navigation and visible focus;
- contrast, labels, semantics, and reduced motion where applicable;
- loading, empty, error, success, disabled, and overflow states;
- console/network errors and layout shifts;
- comparison against the accepted design contract.

Record screenshots only when they materially demonstrate acceptance; do not treat screenshots as a substitute for interaction checks.
