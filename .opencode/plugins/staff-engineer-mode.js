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
const bootstrapTemplatePath = path.join(skillsDir, "staff-engineer-mode", "references", "bootstrap-context.md");

const renderTemplate = (template, values) =>
  Object.entries(values).reduce(
    (rendered, [key, value]) => rendered.replaceAll(`{{${key}}}`, value),
    template,
  );

const getBootstrapContent = () => {
  if (!fs.existsSync(routerPath) || !fs.existsSync(bootstrapTemplatePath)) {
    return null;
  }

  const bootstrapTemplate = fs.readFileSync(bootstrapTemplatePath, "utf8");
  const toolMapping = `**Tool Mapping for OpenCode:**
When Staff Engineer Mode skills reference tools you do not have, substitute OpenCode equivalents:
- \`Skill\` tool -> OpenCode's native \`skill\` tool
- \`Task\` tool with subagents -> OpenCode's subagent system (@mention)
- File operations and shell commands -> your native OpenCode tools

Use OpenCode's native \`skill\` tool only for the router. After routing, read the selected specialist reference file from \`${specialistsDir}/<slug>.md\`.`;

  return renderTemplate(bootstrapTemplate, {
    SPECIALIST_ROOT: specialistsDir,
    ROUTER_PATH: routerPath,
    EVENT_HOOK: path.resolve(__dirname, "..", "..", "hooks", "agent-event-policy"),
    CURRENT_REPO: "",
    TOOL_MAPPING: toolMapping,
  });
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
