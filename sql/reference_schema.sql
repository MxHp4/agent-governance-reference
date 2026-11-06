-- Synthetic reference schema. No production data or proprietary identifiers.

create type agent_risk_tier as enum ('read_only', 'draft', 'human_approved');
create type run_status as enum ('queued', 'running', 'waiting_review', 'succeeded', 'failed', 'rolled_back');
create type review_status as enum ('pending', 'approved', 'rejected', 'expired');

create table agent_registry (
  agent_id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  owner text not null,
  risk_tier agent_risk_tier not null,
  enabled boolean not null default false,
  evaluation_version text not null,
  created_at timestamptz not null default now()
);

create table tool_grants (
  grant_id uuid primary key default gen_random_uuid(),
  agent_id uuid not null references agent_registry(agent_id),
  tool_name text not null,
  allowed_actions text[] not null default '{}',
  forbidden_fields text[] not null default '{}',
  unique (agent_id, tool_name)
);

create table agent_runs (
  run_id uuid primary key default gen_random_uuid(),
  agent_id uuid not null references agent_registry(agent_id),
  idempotency_key text not null unique,
  status run_status not null default 'queued',
  input_digest text not null,
  output_digest text,
  error_class text,
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz not null default now()
);

create table review_requests (
  review_id uuid primary key default gen_random_uuid(),
  run_id uuid not null references agent_runs(run_id),
  requested_action jsonb not null,
  status review_status not null default 'pending',
  decided_by text,
  decision_note text,
  decided_at timestamptz,
  expires_at timestamptz not null
);

create table audit_events (
  event_id bigint generated always as identity primary key,
  run_id uuid not null references agent_runs(run_id),
  event_type text not null,
  actor text not null,
  payload jsonb not null default '{}',
  created_at timestamptz not null default now()
);

-- Public clients never receive direct access to control-plane rows.
alter table agent_registry enable row level security;
alter table tool_grants enable row level security;
alter table agent_runs enable row level security;
alter table review_requests enable row level security;
alter table audit_events enable row level security;

-- Consequential writes are performed only by a trusted server-side role.
-- No policy is included here because deployment-specific identity mapping is required.

comment on table tool_grants is 'Least-privilege grants; forbidden_fields is enforced before execution.';
comment on table review_requests is 'Human approval is a durable state transition, not a prompt instruction.';
comment on table audit_events is 'Append-only reconstruction trail for prompts, tools, decisions, and outcomes.';
