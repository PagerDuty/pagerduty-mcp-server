/**
 * PagerDuty Logo Component - Official PagerDuty Icon
 */

import logoSvg from "../assets/pagerduty-icon.svg";

interface PagerDutyLogoProps {
  size?: number;
}

export function PagerDutyLogo({ size = 36 }: PagerDutyLogoProps) {
  return (
    <img
      src={logoSvg}
      alt="PagerDuty"
      width={size}
      height={size}
      style={{ display: "block" }}
    />
  );
}
