# Final review regression checks

Prepared November 15, 2026 for Thomas Boyle's review contribution.

## Reproduced before fixes

- Denver dinner with $25/person and rideshare returned $28/person.
- Locking the second stop and regenerating returned two copies of The 1UP Arcade Bar.
- Chat changed the start from 18:00 to 19:00; the next swap reverted it to 18:00.
- Form date validation rejected today's date in America/Denver.
- Frontend code kept form preferences instead of the Surprise Me generation payload.

## Regression checks

- Backend suite: 72 tests. New coverage includes rideshare budget edges,
  second/multiple locks, infeasible locks, sequential HTTP edits, duplicate
  model selections, unknown costs, and adding a stop to an empty plan.
- Frontend suite: 4 UI tests with the actual planner form and page, using a
  stubbed API. Covers Surprise Me → edit → save, chat change → form draft
  change → swap, locks following reordered venues, and today/custom dietary
  text → generate → edit. Tests run in America/Denver in CI.
- Frontend production build is included in validation.

The tests do not call live GenAI/Google APIs. They do not establish live venue
hours, dietary suitability, ticket availability, actual prices or audio playback.

## Human checks still required

1. Start a clean extracted final archive using README instructions.
2. Configure the course planning/image/speech endpoints and test the real app
   in a normal browser. Play and download a voice-over; view/download a poster.
3. Rehearse sequential edits, second/last/multiple locks, low budgets,
   after-midnight plans, Surprise Me, save/load, sharing, and mobile layout.
4. Confirm slide 7's actual tools/models with teammates; complete slide 11's
   contributions and presentation assignments. No missing roles were invented.
5. Update presentation test totals to 72 backend + 4 frontend tests and rehearse
   the 10–12-minute presentation. Export the final repository after merging fixes.

Current limitations: no-key generation is deterministic and conversational
controls need the planning AI; demo cities are limited; dietary and opening-hour
suitability are not independently verified; localhost links require a locally
running app. No public deployment is required by the supplied assignment.
