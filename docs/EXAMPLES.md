# Engineering Decision Logger Examples

This document provides various usage examples for EDL.

## 1. Logging a New Decision

Run the `log` command to start the interactive wizard:

```bash
edl log
```

**Interactive Prompts:**
- **Title:** Use a clear, action-oriented title (e.g., "Use PostgreSQL for main data storage").
- **Context:** Describe the current situation and why a decision is needed.
- **Decision Drivers:** List the main factors influencing the decision (e.g., scalability, cost, team expertise).
- **Options:** List the alternatives considered (e.g., Option A: MySQL, Option B: PostgreSQL).
- **Chosen Option:** Specify which option was selected.
- **Rationale:** Explain why the chosen option was selected over the others.
- **Consequences:** Detail the positive and negative impacts of this decision.

## 2. Searching Decisions

You can search through all recorded decisions using keywords:

```bash
edl search "PostgreSQL"
```

This will search in titles, contexts, rationales, and chosen options.

## 3. Listing and Showing Decisions

To see a list of all decisions:

```bash
edl list
```

To see the full details of a specific decision by its ID:

```bash
edl show 1
```

## 4. Git Integration

Install the Git pre-commit hook to ensure decisions are tracked alongside your code changes:

```bash
edl install-hooks
```

Once installed, EDL will automatically try to capture the current Git commit hash when you log a new decision.
