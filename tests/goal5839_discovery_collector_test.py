from __future__ import annotations

import json
import unittest
import urllib.parse

from scripts import goal5839_collect_discovery_search_results as collector


class Goal5839DiscoveryCollectorTest(unittest.TestCase):
    def test_github_projection_preserves_rank_and_only_frozen_fields(self) -> None:
        payload = json.dumps(
            {
                "total_count": 1,
                "incomplete_results": False,
                "items": [
                    {
                        "id": 7,
                        "node_id": "R_7",
                        "full_name": "owner/repo",
                        "html_url": "https://github.com/owner/repo",
                        "owner": {"login": "owner", "secret": "drop"},
                        "fork": False,
                        "archived": False,
                        "default_branch": "main",
                        "created_at": "2020-01-01T00:00:00Z",
                        "updated_at": "2026-01-01T00:00:00Z",
                        "pushed_at": "2026-01-01T00:00:00Z",
                        "description": "paper code",
                        "private": False,
                    }
                ],
            }
        ).encode()
        result = collector._parse_github(payload)
        self.assertEqual(result["returned_item_count"], 1)
        self.assertEqual(result["items"][0]["rank"], 1)
        self.assertEqual(result["items"][0]["owner_login"], "owner")
        self.assertNotIn("secret", result["items"][0])
        self.assertNotIn("private", result["items"][0])

    def test_duckduckgo_parser_preserves_result_order_and_decodes_redirect(self) -> None:
        target = "https://github.com/owner/repo?a=1&b=2"
        redirect = "//duckduckgo.com/l/?" + urllib.parse.urlencode({"uddg": target})
        payload = (
            '<html><a class="noise" href="https://example.invalid">x</a>'
            f'<a class="result__a" href="{redirect}">First &amp; Result</a>'
            '<a class="result__a" href="https://example.org/two">Second</a></html>'
        ).encode()
        result = collector._parse_general(payload)
        self.assertEqual(result["returned_item_count"], 2)
        self.assertEqual(result["items"][0], {"rank": 1, "title": "First & Result", "url": target})
        self.assertEqual(result["items"][1]["rank"], 2)

    def test_frozen_urls_have_exact_query_and_pagination(self) -> None:
        github = collector._github_url("https://api.github.com/search/repositories", '"T" in:readme')
        github_query = urllib.parse.parse_qs(urllib.parse.urlparse(github).query)
        self.assertEqual(github_query, {"q": ['"T" in:readme'], "page": ["1"], "per_page": ["50"]})
        general = collector._general_url("https://html.duckduckgo.com/html/", '"T" "source code"')
        self.assertEqual(
            urllib.parse.parse_qs(urllib.parse.urlparse(general).query),
            {"q": ['"T" "source code"']},
        )

    def test_binding_identity_and_zero_result_state_validate(self) -> None:
        binding = collector._load_binding()
        self.assertEqual(binding["preregistration"]["work_count"], 29)
        self.assertTrue(all(value == 0 for value in binding["execution_state"].values()))


if __name__ == "__main__":
    unittest.main()
