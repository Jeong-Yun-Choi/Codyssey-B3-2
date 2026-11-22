import unittest
import contextlib
import io
import sys
from pathlib import Path
from unittest.mock import patch

from src.prompt_builder import build_prompt
from src.safety import mask_git_info


class BonusTests(unittest.TestCase):
    def setUp(self):
        self.info = {
            "status": " M README.md",
            "diff": "+first\n+second\n+third\n",
            "staged_diff": "+one\n+two\n",
            "untracked_files": {},
        }

    def test_convention_changes_only_opt_in_prompt(self):
        normal = build_prompt(self.info, "commit")
        customized = build_prompt(self.info, "commit", convention="docs")
        self.assertNotIn("docs:", normal)
        self.assertIn("docs:", customized)

    def test_safe_limit_truncates_both_diffs_without_mutating_original(self):
        limited = mask_git_info(self.info, max_diff_lines=1)
        self.assertIn("+first", limited["diff"])
        self.assertNotIn("+second", limited["diff"])
        self.assertIn("+one", limited["staged_diff"])
        self.assertNotIn("+two", limited["staged_diff"])
        self.assertIn("생략", limited["diff"])
        self.assertIn("+second", self.info["diff"])

    def test_short_new_files_do_not_exhaust_total_limit(self):
        self.info["untracked_files"] = {f"{i}.txt": "a" for i in range(6)}
        prompt = build_prompt(self.info, "pr")
        self.assertIn("파일: 5.txt\na", prompt)
        self.assertNotIn("[본문 생략: 전체 프롬프트 한도 초과]", prompt)

    def test_cli_applies_convention_and_safe_limit_to_request(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
        try:
            import main

            self.info["diff"] = '+email="dev@example.com"\n+secret="fake-secret"\n'
            self.info["skipped_files"] = {}
            args = ["main.py", "commit", "--safe-mode", "--safe-max-diff-lines", "1", "--convention", "docs"]
            with patch.object(sys, "argv", args), \
                 patch.object(main, "collect_git_info", return_value=self.info), \
                 patch("ai_client.get_api_key", return_value="fake-key"), \
                 patch("ai_client.requests.post") as fake_post, \
                 contextlib.redirect_stdout(io.StringIO()):
                fake_post.return_value.json.return_value = {
                    "content": [{"type": "text", "text": "docs: 문서 갱신"}],
                    "stop_reason": "end_turn",
                }
                main.main()
                prompt = fake_post.call_args.kwargs["json"]["messages"][0]["content"]
                self.assertIn("docs:", prompt)
                self.assertIn("[이메일 가림]", prompt)
                self.assertNotIn("dev@example.com", prompt)
                self.assertNotIn("fake-secret", prompt)
                self.assertIn("[나머지 diff 생략]", prompt)
        finally:
            sys.path.pop(0)


if __name__ == "__main__":
    unittest.main()
