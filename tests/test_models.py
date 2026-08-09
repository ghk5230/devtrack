import unittest

from issues.models import (
    CriticalIssue,
    Issue,
    LowPriorityIssue,
    Reporter,
)


class EntityTests(unittest.TestCase):
    def test_reporter_serializes_and_validates(self):
        reporter = Reporter(1, "Asha Rao", "asha@example.com", "backend")
        reporter.validate()
        self.assertEqual(reporter.to_dict()["team"], "backend")

    def test_reporter_rejects_empty_name(self):
        reporter = Reporter(1, "", "asha@example.com", "backend")
        with self.assertRaisesRegex(ValueError, "Name cannot be empty"):
            reporter.validate()

    def test_reporter_rejects_invalid_email(self):
        reporter = Reporter(1, "Asha Rao", "invalid-email", "backend")
        with self.assertRaisesRegex(ValueError, "Invalid email"):
            reporter.validate()

    def test_issue_rejects_invalid_status(self):
        issue = Issue(1, "Broken login", "Details", "pending", "high", 1)
        with self.assertRaisesRegex(ValueError, "Status must be one of"):
            issue.validate()

    def test_issue_rejects_invalid_priority(self):
        issue = Issue(1, "Broken login", "Details", "open", "urgent", 1)
        with self.assertRaisesRegex(ValueError, "Priority must be one of"):
            issue.validate()

    def test_priority_subclasses_override_describe(self):
        critical = CriticalIssue(1, "Broken login", "Details", "open", "critical", 1)
        low = LowPriorityIssue(2, "Minor typo", "Details", "open", "low", 1)
        self.assertIn("[URGENT]", critical.describe())
        self.assertIn("low priority", low.describe())


if __name__ == "__main__":
    unittest.main()
