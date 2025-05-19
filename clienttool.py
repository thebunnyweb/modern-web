import 'dotenv/config.js';
import { experimental_createMCPClient, generateText } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';

// Point to your vLLM endpoint (OpenAI-compatible):
const openai = createOpenAI({
  baseURL: process.env.OPENAI_API_BASE || 'http://localhost:8001/v1',
  apiKey:  process.env.OPENAI_API_KEY || 'sk-no-key',  // vLLM ignores the key
});

const SYSTEM = (tools) => `
You are a helpful assistant with access to these tools:
${tools.map(t => `- ${t.name}: ${t.description || ''}`).join('\n')}

When you must use a tool, respond with ONLY:

<TOOL_CALL>{
  "name": "<tool_name>",
  "arguments": { ... }
}</TOOL_CALL>

If no tool is needed, answer normally. Never output anything else inside <TOOL_CALL> tags.
`;

(async () => {
  /* 1. Connect to the MCP server */
  const mcpClient = await experimental_createMCPClient({
    transport: { type: 'sse', url: process.env.MCP_SSE_URL || 'http://localhost:8000/sse' }
  });
  const tools = await mcpClient.tools();        // ↩️ AI-SDK-compatible tool objects

  /* 2. Conversation loop */
  const messages = [
    { role: 'system',    content: SYSTEM(tools) },
    { role: 'user',      content: 'Give me the titles of 3 todos.' }
  ];

  const first = await generateText({ model: openai('meta-llama-3-70b'), messages });

  // 3. Did the model obey the <TOOL_CALL> contract?
  const match = first.text.match(/<TOOL_CALL>([\s\S]+?)<\/TOOL_CALL>/);
  if (match) {
    const { name, arguments: args } = JSON.parse(match[1]);
    const tool = tools.find(t => t.name === name);
    if (!tool) throw new Error(`Unknown tool ${name}`);

    const result = await tool.call(args);       // 🔧 run the MCP tool

    messages.push({ role: 'assistant', content: first.text });
    messages.push({ role: 'tool', name, content: JSON.stringify(result) });

    const final = await generateText({ model: openai('meta-llama-3-70b'), messages });
    console.log('\n=== FINAL ANSWER ===\n', final.text);
  } else {
    console.log(first.text);                    // Fallback if no tool-call
  }

  await mcpClient.close();
})();