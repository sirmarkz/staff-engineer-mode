#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / ".opencode" / "plugins" / "staff-engineer-mode.js"


class OpenCodePluginTests(unittest.TestCase):
    def run_node(self, source: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["node", "--input-type=module", "--eval", source],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_transform_ignores_malformed_messages_and_injects_first_user(self) -> None:
        source = textwrap.dedent(
            f"""
            import assert from "node:assert/strict";
            import pluginFactory from {PLUGIN.as_uri()!r};

            const plugin = await pluginFactory();
            const output = {{
              messages: [
                {{}},
                {{ info: {{ role: "assistant" }}, parts: [{{ type: "text", text: "ready" }}] }},
                {{ info: {{ role: "user" }}, parts: [{{ type: "text", text: "build this" }}] }},
              ],
            }};

            await plugin["experimental.chat.messages.transform"]({{}}, output);

            const user = output.messages[2];
            assert.equal(user.parts[0].type, "text");
            assert.match(user.parts[0].text, /You have staff-engineer-mode/);
            assert.equal(user.parts[1].text, "build this");
            """
        )

        result = self.run_node(source)

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_transform_noops_when_user_parts_are_missing(self) -> None:
        source = textwrap.dedent(
            f"""
            import pluginFactory from {PLUGIN.as_uri()!r};

            const plugin = await pluginFactory();
            const output = {{ messages: [{{ info: {{ role: "user" }} }}] }};

            await plugin["experimental.chat.messages.transform"]({{}}, output);
            """
        )

        result = self.run_node(source)

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_transform_ignores_non_string_text_parts(self) -> None:
        source = textwrap.dedent(
            f"""
            import assert from "node:assert/strict";
            import pluginFactory from {PLUGIN.as_uri()!r};

            const plugin = await pluginFactory();
            const output = {{
              messages: [
                {{ info: {{ role: "user" }}, parts: [{{ type: "text", text: 42 }}] }},
              ],
            }};

            await plugin["experimental.chat.messages.transform"]({{}}, output);

            const user = output.messages[0];
            assert.match(user.parts[0].text, /You have staff-engineer-mode/);
            assert.equal(user.parts[1].text, 42);
            """
        )

        result = self.run_node(source)

        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
