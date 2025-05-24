export default function ChatMCP() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<CoreMessage[]>([]);
  const [loading, setLoading] = useState(false);

  const queryLLMWithToolLoop = useCallback(async () => {
    setLoading(true);
    let updatedMessages = [...messages];

    while (true) {
      const response = await fetch('/api/mcp', {
        method: 'POST',
        body: JSON.stringify({
          model: '/lab7/labs5/restricted_models/Meta-Llama-3-3-70B-Instruct',
          messages: updatedMessages
        }),
        headers: { 'Content-Type': 'application/json' }
      });

      const result = await response.json();
      const { messages: newMessages, toolResults } = result;

      updatedMessages = newMessages;

      // Break the loop if no further toolResults
      if (!toolResults || toolResults.length === 0) break;
    }

    setMessages(updatedMessages);
    setLoading(false);
  }, [messages]);

  useEffect(() => {
    queryLLMWithToolLoop();
  }, []);

  return (
    <div>
      <input
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={async e => {
          if (e.key === 'Enter') {
            const newUserMessage = { role: 'user', content: input };
            setMessages(prev => [...prev, newUserMessage]);
            setInput('');
            await queryLLMWithToolLoop();
          }
        }}
      />
      {/* You can render messages below */}
    </div>
  );
}