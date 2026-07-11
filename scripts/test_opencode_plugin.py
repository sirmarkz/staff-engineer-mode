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
            import path from "node:path";
            import pluginFactory from {PLUGIN.as_uri()!r};

            const plugin = await pluginFactory();
            const output = {{
              messages: [
                {{}},
                {{ info: {{ role: "assistant" }}, parts: [{{ type: "text", text: "ready" }}] }},
                {{ info: {{ role: "user" }}, parts: [{{ type: "text", text: "build this" }}] }},
              ],
            }};

            const transform = plugin["experimental.chat.messages.transform"];
            await transform({{}}, output);
            await transform({{}}, output);

            const user = output.messages[2];
            assert.equal(user.parts.length, 2);
            assert.equal(user.parts[0].type, "text");
            const bootstrap = user.parts[0].text;
            const fields = Object.fromEntries(
              bootstrap
                .split("\\n")
                .filter((line) => /^[A-Z_]+=/.test(line))
                .map((line) => [
                  line.slice(0, line.indexOf("=")),
                  line.slice(line.indexOf("=") + 1),
                ]),
            );
            assert.deepEqual(
              Object.keys(fields).sort(),
              ["CURRENT_REPO", "EVENT_HOOK", "ROUTER_PATH", "SPECIALIST_ROOT", "TEMPLATE_ROOT"],
            );
            assert.equal(path.basename(fields.ROUTER_PATH), "SKILL.md");
            assert.equal(path.basename(fields.SPECIALIST_ROOT), "specialists");
            assert.equal(path.basename(fields.TEMPLATE_ROOT), "templates");
            assert.equal(fields.CURRENT_REPO, "");
            assert.doesNotMatch(bootstrap, /\{{\{{[^}}]+\}}\}}/);
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

            const transform = plugin["experimental.chat.messages.transform"];
            await transform({{}}, output);
            await transform({{}}, output);

            const user = output.messages[0];
            assert.equal(user.parts.length, 2);
            assert.equal(user.parts[0].type, "text");
            assert.equal(typeof user.parts[0].text, "string");
            assert.equal(user.parts[1].text, 42);
            """
        )

        result = self.run_node(source)

        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
