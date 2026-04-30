// src/components/InfoIcon.tsx

interface Props {
  text: string;
}

export function InfoIcon({ text }: Props) {
  return (
    <span className="info-icon" title={text} aria-label={text}>
      ⓘ
    </span>
  );
}
