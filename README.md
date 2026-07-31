# Epistemic Friction

**Conversational Inertia and Epistemic Calibration**

Epistemic Friction is an open, falsifiable experimental framework for testing whether an AI assistant can increase a user's confidence more than it improves the quality of the user's reasons.

This repository is the **First Stone v0.1**. It does not contain study results and makes no empirical claim.

## What is already real

- one complete synthetic decision case;
- a balanced, machine-readable Fact Registry;
- deterministic evidence plans for:
  - Continuity: 70/30;
  - Neutral: 50/50;
  - Friction: 30/70;
  - Static Neutral: 50/50;
- an auditable validation command;
- an integrity manifest;
- automated tests, including tamper detection.

## Run

Requires Python 3.11 or newer.

```bash
python -m pip install -e .
epistemic-friction-validate
python -m unittest discover -s tests -v
```

Without installation:

```bash
PYTHONPATH=src python -m epistemic_friction.validate
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Current boundary

The code validates the experimental materials. It does **not** yet:

- call a language model;
- recruit or manage participants;
- score human responses;
- establish that conversational inertia exists.

The next milestone is a dry-run harness that renders the four conditions from the registered facts without permitting the model to invent evidence.
