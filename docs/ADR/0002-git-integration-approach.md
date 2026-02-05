# 2-Git Integration Approach

* Status: Accepted
* Date: 2026-02-05

## Context and Problem Statement

We want to associate decisions with the code changes they refer to.

## Decision Drivers


* Traceability

* Automation


## Considered Options


* Git Hooks

* Manual association

* Commit message parsing


## Decision Outcome

Chosen option: "Git Hooks + Commit Hash storage", because Automatically capturing the current commit hash provides a direct link between the decision and the codebase state.

### Consequences

* Good: Automatic traceability.
* Bad: Requires git repository to be initialized.

## Pros and Cons of the Options

