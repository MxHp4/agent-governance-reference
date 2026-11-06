"""Small, dependency-free policy kernel for the reference implementation."""

from dataclasses import dataclass
from typing import FrozenSet, Mapping


@dataclass(frozen=True)
class ToolGrant:
    tool_name: str
    allowed_actions: FrozenSet[str]
    forbidden_fields: FrozenSet[str]


@dataclass(frozen=True)
class Decision:
    allowed: bool
    requires_review: bool
    reason: str


def authorize(
    *,
    grant: ToolGrant,
    action: str,
    payload: Mapping[str, object],
    risk_tier: str,
) -> Decision:
    """Authorize a proposed action without calling a tool or a model."""
    if action not in grant.allowed_actions:
        return Decision(False, False, "action_not_granted")

    forbidden = grant.forbidden_fields.intersection(payload.keys())
    if forbidden:
        return Decision(False, False, "forbidden_field:" + ",".join(sorted(forbidden)))

    if risk_tier == "read_only" and action != "read":
        return Decision(False, False, "read_only_tier")

    if risk_tier == "human_approved":
        return Decision(True, True, "review_required")

    return Decision(True, False, "allowed")
