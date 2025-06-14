import React from "react";
import "./wave.css"; // we'll create this

const text = "Generating image...";

export default function GeneratingText() {
  return (
    <div className="flex space-x-0.5">
      {text.split("").map((char, i) => (
        <span
          key={i}
          className="text-muted-foreground font-medium wave"
          style={{ animationDelay: `${i * 0.05}s` }}
        >
          {char}
        </span>
      ))}
    </div>
  );
}