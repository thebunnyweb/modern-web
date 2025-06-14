import { useState, useEffect } from "react";

export default function TypingLoader() {
  const text = "Generating image...";
  const [displayed, setDisplayed] = useState("");

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setDisplayed(text.slice(0, i + 1));
      i++;
      if (i === text.length) clearInterval(interval);
    }, 60); // typing speed
    return () => clearInterval(interval);
  }, []);

  return (
    <span className="font-medium text-muted-foreground">
      {displayed}
      <span className="animate-pulse">|</span>
    </span>
  );
}