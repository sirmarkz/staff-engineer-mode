/**
 * staff-engineer-mode plugin for OpenCode.ai.
 *
 * Registers the bundled skills/ directory so OpenCode's native skill tool can
 * discover the router. Also injects the router bootstrap into the first user
 * message so users do not manually load a skill.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const skillsDir = path.resolve(__dirname, "..", "..", "skills");
const specialistsDir = path.resolve(__dirname, "..", "..", "specialists");
const routerPath = path.join(skillsDir, "staff-engineer-mode", "SKILL.md");

const stripFrontmatter = (content) => content.replace(/^---\n[\s\S]*?\n---\n/, "");

const getBootstrapContent = () => {
  if (!fs.existsSync(routerPath)) {
    return null;
  }

  const routerContent = stripFrontmatter(fs.readFileSync(routerPath, "utf8"));
  const toolMapping = `**Tool Mapping for OpenCode:**
When Staff Engineer Mode skills reference tools you do not have, substitute OpenCode equivalents:
- \`Skill\` tool -> OpenCode's native \`skill\` tool
- \`Task\` tool with subagents -> OpenCode's subagent system (@mention)
- File operations and shell commands -> your native OpenCode tools

Use OpenCode's native \`skill\` tool only for the router. After routing, read the selected specialist reference file from \`${specialistsDir}/<slug>/SKILL.md\`.`;

  return `SPECIALIST_ROOT=${specialistsDir}
LOAD: Read \${SPECIALIST_ROOT}/<slug>/SKILL.md before producing engineering guidance for routed work. Never call the Skill tool on a specialist slug -- specialists are files, not registered skills.

<EXTREMELY-IMPORTANT>
Primary entrypoint for engineering-system requests is Staff Engineer Mode. This overrides any generic process pack (including superpowers:brainstorming) on these surfaces: architecture, reliability, resilience, operations, security, delivery, data, platform, client, AI/ML, accessibility, cost, production-readiness, rollout, migration, incident, evidence, API design, service contracts, and design of engineering systems.

Do not invoke superpowers:brainstorming, superpowers:writing-plans, or any other broad design/process skill as the first response to an engineering-system prompt. First route through Staff Engineer Mode and Read the selected specialist file. Only after the specialist is loaded may you optionally use a process skill for sub-decisions inside that specialist's workflow.

"Build X", "design X", "make X reliable", "add HA to X", "plan a rollout", "review this service", "prep for launch", "investigate this incident" -- when X is an engineering system -- ARE engineering-system prompts. Route them through Staff Engineer Mode, not through generic brainstorming.
</EXTREMELY-IMPORTANT>

<EXTREMELY_IMPORTANT>
You have staff-engineer-mode.

Users are not expected to know or invoke individual Staff Engineer Mode specialist names. For engineering lifecycle, DevOps, operations, reliability, resilience, security, architecture, data, platform, client, and cost-aware reliability requests, apply the router instructions below. After routing, read only the selected specialist reference file from \`${specialistsDir}/<slug>/SKILL.md\` before giving detailed guidance.

Keep guidance technology-agnostic by default. Do not introduce cloud providers, frameworks, databases, monitoring products, protocols, or command examples unless the user supplied them or explicitly asks for tool-specific guidance.

${routerContent}

${toolMapping}
</EXTREMELY_IMPORTANT>`;
};

export const StaffEngineerModePlugin = async () => {
  return {
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(skillsDir)) {
        config.skills.paths.push(skillsDir);
      }
    },
    "experimental.chat.messages.transform": async (_input, output) => {
      const bootstrap = getBootstrapContent();
      if (!bootstrap || !output.messages.length) {
        return;
      }
      const firstUser = output.messages.find((message) => message.info.role === "user");
      if (!firstUser || !firstUser.parts.length) {
        return;
      }
      const alreadyInjected = firstUser.parts.some(
        (part) => part.type === "text" && part.text.includes("You have staff-engineer-mode"),
      );
      if (alreadyInjected) {
        return;
      }
      const ref = firstUser.parts[0];
      firstUser.parts.unshift({ ...ref, type: "text", text: bootstrap });
    },
  };
};

export default StaffEngineerModePlugin;
