# Governed Agent Execution Reference

A small, synthetic reference implementation for trustworthy AI operations on Postgres.

This repository demonstrates the control plane around an agent runtime: durable work, human review, least-privilege tool grants, reconstructable audit logs, and evaluation gates. It is intentionally designed as a public portfolio artifact for the **AI Platform Engineer** problem space.

## What this is

- A generic architecture pattern, not a Supabase internal system.
- A synthetic schema and test corpus with no production rows.
- A concrete example of making unsafe actions impossible by construction.
- A starting point for a larger runtime, not a claim of production readiness.

## What this is not

- It does not contain credentials, keys, customer data, contact data, financial records, internal URLs, proprietary prompts, live identifiers, or copied internal schemas.
- It does not connect to or export data from any external project.
- It does not implement autonomous writes to a system of record.

## Design thesis

An agent should be treated as a governed workflow, not as a chat completion. Every run has an owner, risk tier, tool grant, durable state, evaluation status, and an auditable decision trail. The dangerous capability has no code path: the example `record_update` tool can draft a change, but it cannot write an owner, due date, or status.

```text
Event -> Queue -> Runtime -> Tool Gate -> Review Gate -> Commit/Reject
             |       |           |             |             |
             +-------+-----------+-------------+-------------+--> Audit log
                         
                 Evaluation gate blocks promotion
```

## Repository map

- `sql/reference_schema.sql` — synthetic Postgres schema with RLS, risk tiers, review states, and audit records.
- `src/policy.py` — pure-Python policy decisions for tool grants and forbidden fields.
- `evals/golden_cases.jsonl` — small behavioral suite covering safety, provenance, and review behavior.
- `.github/workflows/eval.yml` — CI gate that runs the policy checks and corpus validation.

## How to run

```bash
python -m unittest discover -s src -p 'test_*.py' -v
```

No network, credentials, hosted service, or model API is required.

## Safe extension path

A production version would add an event-triggered queue, a model-agnostic runtime adapter, durable retry/rollback semantics, structured tracing, cost attribution, and a judge-backed evaluation service. Those integrations should be added behind explicit interfaces and reviewed against the same risk-tier policy.

## License

MIT. The examples are provided for educational and portfolio use.
