// sse-to-dataStream.ts
import { createParser, ParsedEvent } from 'eventsource-parser';

export const sseToDataStreamFetch: typeof fetch = async (url, init) => {
  // 1 ▸ Forward the real request to the back-end
  const backendRes = await fetch(url, init);

  // If anything goes wrong, hand the response back unchanged
  if (!backendRes.ok || !backendRes.body) return backendRes;

  // 2 ▸ We will pipe backendRes.body → TransformStream → SDK
  const { readable, writable } = new TransformStream();
  const writer   = writable.getWriter();
  const encoder  = new TextEncoder();

  const write = (code: string, payload: unknown) =>
    writer.write(encoder.encode(`${code}:${JSON.stringify(payload)}\n`));

  // 3 ▸ Parse the SSE as it arrives
  const parser = createParser((e: ParsedEvent) => {
    if (e.type !== 'event') return;

    // e.event comes from backend (“status”, “response”, “token”, …)
    const payload = JSON.parse(e.data);

    switch (e.event) {
      case 'status':             // map to metadata   (TYPE 2)
        write('2', payload);
        break;
      case 'response':           // map to full msg   (TYPE 1)
        write('1', { role: 'assistant', content: payload.content });
        break;
      case 'token':              // optional typing   (TYPE 0)
        write('0', payload.text); // payload.text must already be a string
        break;
      // extend here when backend later adds “image”, “citation”, …
    }
  });

  // 4 ▸ Pump bytes from backend → parser
  (async () => {
    const reader = backendRes.body.getReader();
    const dec    = new TextDecoder();
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      parser.feed(dec.decode(value));
    }
    write('d', { finishReason: 'stop' }); // graceful end  (TYPE d)
    writer.close();
  })();

  // 5 ▸ Return a new Response that the SDK can parse
  return new Response(readable, {
    headers: {
      'X-Vercel-AI-Data-Stream': 'v1',
      'Content-Type': 'application/x-ndjson',
    },
  });
};