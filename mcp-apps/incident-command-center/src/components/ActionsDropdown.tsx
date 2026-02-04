/**
 * More Actions Dropdown Component - Slack-style action menu
 */

import { useState, useRef, useEffect } from "react";

interface DropdownAction {
  label: string;
  onClick: () => void;
  icon?: string;
  disabled?: boolean;
}

interface ActionsDropdownProps {
  actions: DropdownAction[];
  disabled?: boolean;
}

export function ActionsDropdown({ actions, disabled }: ActionsDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isOpen]);

  return (
    <div className="actions-dropdown" ref={dropdownRef} onClick={(e) => e.stopPropagation()}>
      <button
        className="action-btn dropdown-trigger"
        onClick={(e) => {
          e.stopPropagation();
          setIsOpen(!isOpen);
        }}
        disabled={disabled}
      >
        More actions ▼
      </button>
      {isOpen && (
        <div className="dropdown-menu" onClick={(e) => e.stopPropagation()}>
          {actions.map((action, index) => (
            <button
              key={index}
              className="dropdown-item"
              onClick={(e) => {
                e.stopPropagation();
                action.onClick();
                setIsOpen(false);
              }}
              disabled={action.disabled}
            >
              {action.icon && <span className="dropdown-icon">{action.icon}</span>}
              <span>{action.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
