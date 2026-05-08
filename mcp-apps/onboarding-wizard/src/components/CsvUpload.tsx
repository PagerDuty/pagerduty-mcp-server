import { useState } from "react";
import type { UserFormData } from "../types.js";

interface Props {
  onImport: (users: UserFormData[]) => void;
}

const SCHEMA = "name,email,role,time_zone\nAlice Johnson,alice@example.com,user,America/New_York";

const VALID_ROLES = new Set(["admin", "limited_user", "observer", "owner", "read_only_user", "restricted_access", "read_only_limited_user", "user"]);

function parseCSV(text: string): UserFormData[] {
  const lines = text.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const header = lines[0].split(",").map((h) => h.trim().toLowerCase());
  const nameIdx = header.indexOf("name");
  const emailIdx = header.indexOf("email");
  const roleIdx = header.indexOf("role");
  const tzIdx = header.indexOf("time_zone");

  return lines.slice(1).flatMap((line) => {
    const cols = line.split(",").map((c) => c.trim());
    const name = nameIdx >= 0 ? cols[nameIdx] : "";
    const email = emailIdx >= 0 ? cols[emailIdx] : "";
    const role = roleIdx >= 0 && VALID_ROLES.has(cols[roleIdx]) ? cols[roleIdx] : "user";
    const time_zone = tzIdx >= 0 && cols[tzIdx] ? cols[tzIdx] : "UTC";
    if (!name || !email) return [];
    return [{ name, email, role, time_zone }];
  });
}

export function CsvUpload({ onImport }: Props) {
  const [open, setOpen] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [count, setCount] = useState<number | null>(null);

  function handleFile(file: File) {
    setError(null);
    setCount(null);
    if (!file.name.endsWith(".csv")) {
      setError("Please upload a .csv file.");
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const users = parseCSV(text);
      if (users.length === 0) {
        setError("No valid rows found. Check column headers: name, email, role, time_zone.");
        return;
      }
      setCount(users.length);
      onImport(users);
    };
    reader.readAsText(file);
  }

  return (
    <div className="csv-section">
      <button className="csv-toggle" onClick={() => setOpen((v) => !v)}>
        {open ? "▲" : "▼"} Bulk import users via CSV
      </button>
      {open && (
        <div className="csv-panel">
          <p style={{ fontSize: 12, color: "var(--color-text-muted)", marginBottom: 6 }}>
            CSV schema (required headers):
          </p>
          <pre className="csv-schema">{SCHEMA}</pre>
          <p style={{ fontSize: 11, color: "var(--color-text-muted)", marginBottom: 8 }}>
            Valid roles: user, admin, limited_user, observer, owner, read_only_user, restricted_access, read_only_limited_user
          </p>
          {error && <div className="error-banner">{error}</div>}
          {count !== null && !error && (
            <div className="badge badge-success" style={{ marginBottom: 8 }}>
              {count} user{count !== 1 ? "s" : ""} ready to import
            </div>
          )}
          <div
            className={`csv-drop-zone${dragOver ? " drag-over" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragOver(false);
              const file = e.dataTransfer.files[0];
              if (file) handleFile(file);
            }}
            onClick={() => document.getElementById("csv-file-input")?.click()}
          >
            <input
              id="csv-file-input"
              type="file"
              accept=".csv"
              onChange={(e) => {
                const file = (e.target as HTMLInputElement).files?.[0];
                if (file) handleFile(file);
              }}
            />
            <p className="csv-drop-label">
              Drag & drop your CSV here, or <span>click to browse</span>
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
