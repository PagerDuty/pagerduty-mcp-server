// src/components/InfoIcon.tsx

import { useRef, useState } from "react";
import { createPortal } from "react-dom";

interface Props {
  text: string;
}

export function InfoIcon({ text }: Props) {
  const [pos, setPos] = useState<{ top: number; left: number } | null>(null);
  const ref = useRef<HTMLSpanElement>(null);

  function show() {
    if (!ref.current) return;
    const r = ref.current.getBoundingClientRect();
    setPos({ top: r.top - 8, left: r.left + r.width / 2 });
  }

  function hide() {
    setPos(null);
  }

  return (
    <>
      <span
        ref={ref}
        className="info-icon"
        onMouseEnter={show}
        onMouseLeave={hide}
        aria-label={text}
      >
        ⓘ
      </span>
      {pos &&
        createPortal(
          <div className="info-tooltip" style={{ top: pos.top, left: pos.left }}>
            {text}
          </div>,
          document.body,
        )}
    </>
  );
}
