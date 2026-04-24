const PALETTE = [
  "#89b4fa", // blue
  "#a6e3a1", // green
  "#cba6f7", // mauve
  "#fab387", // peach
  "#f9e2af", // yellow
  "#94e2d5", // teal
  "#f38ba8", // red
  "#89dceb", // sky
];

export function userColor(userId: string): string {
  let hash = 0;
  for (let i = 0; i < userId.length; i++) {
    hash = (hash * 31 + userId.charCodeAt(i)) & 0xffffffff;
  }
  return PALETTE[Math.abs(hash) % PALETTE.length];
}

// All palette colors are light — dark mantle text works for all
export const USER_COLOR_FG = "#1e1e2e";
