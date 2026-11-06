import json
import pathlib
import unittest

from policy import ToolGrant, authorize


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.grant = ToolGrant(
            tool_name="record_update",
            allowed_actions=frozenset({"read", "draft"}),
            forbidden_fields=frozenset({"owner", "due_date", "status"}),
        )

    def test_read_only_can_read(self):
        decision = authorize(
            grant=self.grant, action="read", payload={"query": "status"}, risk_tier="read_only"
        )
        self.assertEqual((decision.allowed, decision.requires_review), (True, False))

    def test_read_only_cannot_draft(self):
        decision = authorize(
            grant=self.grant, action="draft", payload={"body": "summary"}, risk_tier="read_only"
        )
        self.assertFalse(decision.allowed)

    def test_human_approved_draft_requires_review(self):
        decision = authorize(
            grant=self.grant, action="draft", payload={"body": "proposal"}, risk_tier="human_approved"
        )
        self.assertEqual((decision.allowed, decision.requires_review), (True, True))

    def test_forbidden_commitment_field_has_no_code_path(self):
        decision = authorize(
            grant=self.grant,
            action="draft",
            payload={"owner": "example", "body": "proposal"},
            risk_tier="human_approved",
        )
        self.assertFalse(decision.allowed)
        self.assertIn("forbidden_field", decision.reason)

    def test_ungranted_action_is_denied(self):
        decision = authorize(
            grant=self.grant, action="send", payload={"body": "hello"}, risk_tier="draft"
        )
        self.assertFalse(decision.allowed)

    def test_golden_corpus_matches_policy(self):
        corpus = pathlib.Path(__file__).parents[1] / "evals" / "golden_cases.jsonl"
        for raw in corpus.read_text().splitlines():
            case = json.loads(raw)
            decision = authorize(
                grant=self.grant,
                action=case["action"],
                payload=case["payload"],
                risk_tier=case["risk_tier"],
            )
            expected = case["expected"]
            self.assertEqual(decision.allowed, expected["allowed"], case["name"])
            self.assertEqual(decision.requires_review, expected["requires_review"], case["name"])


if __name__ == "__main__":
    unittest.main()
