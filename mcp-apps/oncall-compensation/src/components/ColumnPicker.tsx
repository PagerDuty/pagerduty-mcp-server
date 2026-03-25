import { useEffect, useRef } from "react";
import { ALL_COLS } from "./CompensationTable";
import type { SortKey } from "./CompensationTable";

interface Props {
  visibleCols: Set<SortKey>;
  onChange: (visibleCols: Set<SortKey>) => void;
  open: boolean;
  onClose: () => void;
}

export function ColumnPicker({ visibleCols, onChange, open, onClose }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    if (!open) return;
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        onClose();
      }
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open, onClose]);

  const toggleCol = (key: SortKey) => {
    const next = new Set(visibleCols);
    if (next.has(key)) {
      next.delete(key);
    } else {
      next.add(key);
    }
    onChange(next);
  };

  const toggleableCols = ALL_COLS.filter((c) => c.toggleable);

  return (
    <div className="col-picker-wrap" ref={ref}>
      {open && (
        <div className="col-picker-dropdown">
          <div className="col-picker-title">Columns</div>
          {toggleableCols.map((col) => {
            const checked = visibleCols.has(col.key);
            return (
              <label key={col.key} className="col-picker-row">
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggleCol(col.key)}
                />
                <span className={checked ? "" : "col-picker-hidden"}>
                  {col.label}
                </span>
              </label>
            );
          })}
        </div>
      )}
    </div>
  );
}
