# SF Bike Theft — portfolio project

## How to work with me here
- **Teach, don't do.** Explain the reasoning, then hand me the command or the
  code and let me type it. Do not create, edit, or delete files unless I
  explicitly ask you to.
- When something breaks, walk me through debugging it — that's the useful part.
- Tell me when something is industry-standard vs. a convention vs. your taste.
- Git: I drive VS Code's Source Control panel. Explain what each step does
  underneath.
- Define technical terms in plain language on first use.

## What this is
A public data-science portfolio piece (audience: a hiring manager who spends
90 seconds on the README and never runs the code). Question: where and when is
it actually risky to lock up a bike in SF — rates, not counts. The denominator
(bikes parked per place-hour) is the project; it's the same problem as
identity resolution in marketing attribution.

## Decisions already made
- Rebuilding from empty, by hand, 2026-08-26. Layout roughly follows
  Cookiecutter Data Science (data/raw is immutable + gitignored + re-fetched
  by a script; data/processed is derived).
- Real requirements.txt with the ~5 packages actually imported, not pip freeze.
- Numerator: SFPD incident reports, DataSF dataset wg3w-h783,
  incident_subcategory = 'Larceny Thef