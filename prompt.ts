import { experimental_mcpClient } from 'ai';

const MCP_URL = process.env.MCP_URL || 'http://localhost:7001'; // Your MCP endpoint

async function generateSystemPrompt() {
  const mcp = experimental_mcpClient({ url: MCP_URL });

  const tools = await mcp.listTools(); // tools: Record<string, Tool>

  const toolSummaries = Object.entries(tools).map(([toolName, tool]) => {
    const schema = tool.parameters?.jsonSchema;
    const requiredArgs = schema?.required || [];
    const props = schema?.properties || {};

    const argDescriptions = requiredArgs.map((argName) => {
      const prop = props[argName];
      const type = prop?.type || 'unknown';
      const desc = prop?.description || 'no description';
      return `- \`${argName}\` (${type}): ${desc}`;
    });

    return `### Tool: \`${toolName}\`
**Description**: ${tool.description}
**Arguments (required)**:
${argDescriptions.join('\n')}

To call this tool, respond **exactly** in this JSON format:
\`\`\`json
{
  "tool": "${toolName}",
  "args": {
    ${requiredArgs.map((arg) => `"${arg}": "..."`).join(',\n    ')}
  }
}
\`\`\``;
  });

  const finalPrompt = `You are an assistant with access to the following tools. When you decide that a tool should be used, respond in JSON with the tool name and arguments exactly as shown.

${toolSummaries.join('\n---\n')}

Only return the JSON.`;

  return finalPrompt;
}

generateSystemPrompt().then((prompt) => {
  console.log('\n==== SYSTEM MESSAGE FOR LLM ====\n');
  console.log(prompt);
});