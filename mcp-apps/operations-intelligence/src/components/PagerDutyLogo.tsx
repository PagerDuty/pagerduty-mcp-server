export function PagerDutyLogo({ size = 24 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="PagerDuty"
    >
      <path
        d="M14.5 2H9.5C6.46 2 4 4.46 4 7.5V22h4v-5h6.5c3.04 0 5.5-2.46 5.5-5.5v-4C20 4.46 17.54 2 14.5 2zM16 11.5c0 .83-.67 1.5-1.5 1.5H8V6h6.5c.83 0 1.5.67 1.5 1.5v4z"
        fill="currentColor"
      />
    </svg>
  );
}
