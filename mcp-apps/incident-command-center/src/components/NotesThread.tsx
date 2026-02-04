/**
 * NotesThread - Conversation-style notes view for incidents
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import { useState } from "react";
import { addIncidentNote } from "../api";

interface Note {
  id: string;
  content: string;
  created_at: string;
  user: {
    summary: string;
  };
}

interface NotesThreadProps {
  app: App;
  incidentId: string;
  notes: Note[];
  onNoteAdded: () => void;
}

function formatTimestamp(iso: string): string {
  const date = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

export function NotesThread({ app, incidentId, notes, onNoteAdded }: NotesThreadProps) {
  const [newNote, setNewNote] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddNote = async () => {
    if (!newNote.trim()) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await addIncidentNote(app, incidentId, newNote);
      setNewNote("");
      onNoteAdded(); // Refresh notes
    } catch (err) {
      setError("Failed to add note. Please try again.");
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleAddNote();
    }
  };

  return (
    <div className="notes-thread">
      <h4>📝 Incident Notes</h4>

      {/* Notes list */}
      <div className="notes-list">
        {notes.length === 0 ? (
          <p className="empty-notes">No notes yet. Add the first one below.</p>
        ) : (
          notes.map((note) => (
            <div key={note.id} className="note">
              <div className="note-header">
                <strong>{note.user.summary}</strong>
                <span className="note-time">{formatTimestamp(note.created_at)}</span>
              </div>
              <p className="note-content">{note.content}</p>
            </div>
          ))
        )}
      </div>

      {/* Add note form */}
      <div className="note-compose">
        <textarea
          value={newNote}
          onChange={(e) => setNewNote(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Add investigation notes... (Ctrl+Enter to submit)"
          disabled={isSubmitting}
          rows={3}
        />
        <button onClick={handleAddNote} disabled={isSubmitting || !newNote.trim()}>
          {isSubmitting ? "Adding..." : "Add Note"}
        </button>
        {error && <p className="error-text">{error}</p>}
      </div>
    </div>
  );
}
