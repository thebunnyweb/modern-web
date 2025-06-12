const multiStepToolRunner = async (parsedJSON, history, systemPrompt, queryLLM, sscClient) => {
  const messages = [...history];

  for (const toolDef of parsedJSON) {
    let toolResults = { content: '', isError: false };

    try {
      toolResults = await sscClient.callTool({
        name: toolDef.tool,
        args: toolDef.args,
      });
    } catch (e) {
      toolResults = { content: `Error: ${e.message}`, isError: true };
    }

    messages.push({
      role: 'assistant',
      content: `Tool (${toolDef.tool}) executed with result: ${toolResults.content?.[0]?.text || toolResults.content}`,
    });

    // Re-query LLM after each tool call to check if additional tool call is required
    const { text } = await queryLLM(systemPrompt, messages);

    // Check if the response indicates further tool calls (assuming JSON structure or plain text)
    let nextTools;
    try {
      nextTools = JSON.parse(text);
    } catch {
      nextTools = null;
    }

    if (nextTools && Array.isArray(nextTools)) {
      // Continue loop if new tools detected
      parsedJSON = nextTools;
    } else {
      // Final text output, append and exit loop
      messages.push({ role: 'assistant', content: text });
      break;
    }
  }

  return messages;
};