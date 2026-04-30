// src/components/CompensationTab.tsx

import type { UserCompensationRecord } from "../api";
import type { SortKey } from "./CompensationTable";
import { CompensationTable } from "./CompensationTable";
import { ColumnPicker } from "./ColumnPicker";
import { SummaryCards } from "./SummaryCards";

interface Props {
  records: UserCompensationRecord[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  sortKey: SortKey;
  sortDir: "asc" | "desc";
  onSort: (key: SortKey) => void;
  visibleCols: Set<SortKey>;
  onVisibleColsChange: (cols: Set<SortKey>) => void;
  colPickerOpen: boolean;
  onColPickerToggle: () => void;
  onColPickerClose: () => void;
  showSummary: boolean;
  onToggleSummary: () => void;
}

export function CompensationTab({
  records,
  selectedId,
  onSelect,
  sortKey,
  sortDir,
  onSort,
  visibleCols,
  onVisibleColsChange,
  colPickerOpen,
  onColPickerToggle,
  onColPickerClose,
  showSummary,
  onToggleSummary,
}: Props) {
  const totalEstimatedPay = records.reduce((s, r) => s + r.estimatedPay, 0);

  return (
    <div className="compensation-tab">
      <div className="controls">
        <button
          className={["btn-summary-toggle", showSummary ? "active" : ""].filter(Boolean).join(" ")}
          onClick={onToggleSummary}
          title={showSummary ? "Hide summary" : "Show summary"}
        >
          {showSummary ? "▲ Summary" : "▼ Summary"}
        </button>
      </div>

      {showSummary && (
        <div className="summary-strip">
          <SummaryCards records={records} totalEstimatedPay={totalEstimatedPay} />
          <div className="summary-actions">
            <div style={{ position: "relative" }}>
              <button
                className={["btn-col-picker", colPickerOpen ? "active" : ""].filter(Boolean).join(" ")}
                onClick={onColPickerToggle}
                title="Show/hide columns"
              >
                ⊞ Columns
              </button>
              <ColumnPicker
                visibleCols={visibleCols}
                onChange={onVisibleColsChange}
                open={colPickerOpen}
                onClose={onColPickerClose}
              />
            </div>
          </div>
        </div>
      )}

      <div className="table-area">
        <CompensationTable
          records={records}
          selectedId={selectedId}
          onSelect={onSelect}
          sortKey={sortKey}
          sortDir={sortDir}
          onSort={onSort}
          visibleCols={visibleCols}
        />
      </div>
    </div>
  );
}
