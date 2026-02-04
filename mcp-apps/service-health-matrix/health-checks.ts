/**
 * PagerDuty Health Check Definitions
 *
 * Organized by object type: Service, Team, User, Escalation Policy, Schedule
 */

export interface HealthCheck {
  id: string;
  object_type: 'Service' | 'Team' | 'User' | 'Escalation Policy' | 'Schedule';
  rule: string;
  urgency: string;
  why: string;
  what: string;
  expected_value: string;
  current_value?: string | number;
  status?: 'pass' | 'fail' | 'warning';
  severity?: 'critical' | 'major' | 'high' | 'medium' | 'low' | 'minor';
}

export const HEALTH_CHECKS: HealthCheck[] = [
  // ESCALATION POLICY CHECKS
  {
    id: 'ep-layers',
    object_type: 'Escalation Policy',
    rule: 'Escalation Policies should have 3 or more layers',
    urgency: 'Critical / Urgent Recommendation',
    why: 'Having less than 3 layers in Escalation Policies increases the risk of missed incidents leading to extended business or customer impact.',
    what: 'Evaluates that Escalation Policies contain more than 3 layers of on-call responders who would receive notifications of incidents.',
    expected_value: '>= 3 layers',
  },
  {
    id: 'ep-loops',
    object_type: 'Escalation Policy',
    rule: 'Escalation Policies should have more than 1 loop',
    urgency: 'Critical / Urgent Recommendation',
    why: 'Having less than 1 repeat (loop) in Escalation Policies increases the risk of missed incidents.',
    what: 'Evaluates that Escalation Policies repeat (loop) the complete escalation configuration more than one time.',
    expected_value: '> 1 loop',
  },
  {
    id: 'ep-inactive-users',
    object_type: 'Escalation Policy',
    rule: 'Escalation Policies should not have inactive users',
    urgency: 'Critical / Urgent Recommendation',
    why: 'Inactive users on Escalation Policies can lead to incidents not being created, resulting in extended outages and business impact.',
    what: 'Represents the condition where one or more inactive users exists on an Escalation Policy.',
    expected_value: '0 inactive users',
  },
  {
    id: 'ep-service-association',
    object_type: 'Escalation Policy',
    rule: 'Escalation policy may be associated with a Service',
    urgency: 'High (4) / Recommendation',
    why: 'Stand alone Escalation Policies may no longer be required and are candidates for removal from PagerDuty.',
    what: 'Evaluates whether Escalation Policies are associated with at least one PagerDuty Technical Service.',
    expected_value: 'Associated with Service',
  },
  {
    id: 'ep-team-association',
    object_type: 'Escalation Policy',
    rule: 'Escalation Policies should be associated with a Team',
    urgency: 'High (4) / Recommendation',
    why: 'Having Team association allows for more accurate Health Check analysis and alerting at the Team level.',
    what: 'Represents the condition where Escalation Policies are not associated with a PagerDuty Team.',
    expected_value: 'Associated with Team',
  },
  {
    id: 'ep-gaps',
    object_type: 'Escalation Policy',
    rule: 'Escalation Policies with Gaps',
    urgency: 'Critical / Urgent Recommendation',
    why: 'Escalation Policies with time gaps could lead to periods where there is no On-Call coverage, creating a critical situation.',
    what: 'Measures how many on-call gaps exist across an Escalation Policy and the total duration of those gaps.',
    expected_value: '0 gaps',
  },

  // SCHEDULE CHECKS
  {
    id: 'schedule-inactive-users',
    object_type: 'Schedule',
    rule: 'Schedules should not have inactive users',
    urgency: 'Critical / Urgent Recommendation',
    why: 'Inactive users on Schedules can lead to incidents not being created, resulting in extended outages and business impact.',
    what: 'Represents the condition where one or more inactive users exist on a Schedule.',
    expected_value: '0 inactive users',
  },

  // USER CHECKS
  {
    id: 'user-contact-methods',
    object_type: 'User',
    rule: 'Responders should have 3 or more contact methods',
    urgency: 'Major / Urgent Recommendation',
    why: 'Having less than 3 contact methods increases the risk of missed incidents.',
    what: 'Users with a responder role have less than 3 contact methods (Phone, SMS, Email, Push, Slack).',
    expected_value: '>= 3 contact methods',
  },
  {
    id: 'user-notification-rules',
    object_type: 'User',
    rule: 'Responders should have 3 or more high-urgency notification rules',
    urgency: 'Major / Urgent Recommendation',
    why: 'Having less than 3 high urgency notification rules increases the risk of missed incidents.',
    what: 'Users with a responder role have less than 3 high-urgency notification rules.',
    expected_value: '>= 3 notification rules',
  },
  {
    id: 'user-staggered-notifications',
    object_type: 'User',
    rule: 'Responders should have staggered high-urgency notification rules',
    urgency: 'Major / Urgent Recommendation',
    why: 'Not having staggered notification rules increases the risk of missed incidents.',
    what: 'Users with a responder role do not have staggered high-urgency notification rules with >= 1-minute delay.',
    expected_value: 'Staggered (>= 1 min delay)',
  },
  {
    id: 'user-active-incidents',
    object_type: 'User',
    rule: 'User Active Incidents Count',
    urgency: 'Varies by count',
    why: 'Responders with multiple active incidents can lead to burnout and delayed response.',
    what: 'Counts the current number of incidents in Active Status (Triggered or Acknowledged) for a User.',
    expected_value: '<= 1 active incident',
  },
  {
    id: 'user-oncall-count',
    object_type: 'User',
    rule: 'User On Call Count',
    urgency: 'Varies by count',
    why: 'Users on call for multiple areas simultaneously can be overwhelmed, increasing burnout risk.',
    what: 'Represents the number of times a User was On Call for multiple areas.',
    expected_value: '<= 3 on-call assignments',
  },

  // TEAM CHECKS
  {
    id: 'team-staggered-notifications-pct',
    object_type: 'Team',
    rule: 'Team responders should have staggered high urgency notification rules %',
    urgency: 'Varies by percentage',
    why: 'Teams with responders not having staggered notification rules increases the risk of missed incidents.',
    what: 'Percentage of Team responders with staggered high-urgency notification rules.',
    expected_value: '>= 90%',
  },
  {
    id: 'team-notification-rules-pct',
    object_type: 'Team',
    rule: 'Team responders should have more than 3 high urgency notification rules %',
    urgency: 'Varies by percentage',
    why: 'Teams with responders having less than 3 notification rules increases missed incident risk.',
    what: 'Percentage of Team responders with 3+ high-urgency notification rules.',
    expected_value: '>= 90%',
  },
  {
    id: 'team-contact-methods-pct',
    object_type: 'Team',
    rule: 'Team Responders should have 3 or more contact methods',
    urgency: 'Varies by percentage',
    why: 'Teams with responders having less than 3 contact methods increases missed incident risk.',
    what: 'Percentage of Team responders with 3+ contact methods.',
    expected_value: '>= 90%',
  },
  {
    id: 'team-transient-incidents',
    object_type: 'Team',
    rule: 'Team Services with Transient Incidents %',
    urgency: 'Varies by percentage',
    why: 'Teams owning Services with high transient incidents face decreased productivity and burnout.',
    what: 'Percentage of Team Services showing transient incidents (auto-resolved <10 min).',
    expected_value: '<= 10%',
  },
  {
    id: 'team-schedules-inactive-users',
    object_type: 'Team',
    rule: 'Team Schedules with Inactive Users %',
    urgency: 'Varies by percentage',
    why: 'Inactive users on Team Schedules can lead to incidents not being created.',
    what: 'Percentage of Team Schedules containing inactive users.',
    expected_value: '0%',
  },
  {
    id: 'team-responders-active-incidents',
    object_type: 'Team',
    rule: 'Team Responders with Active Incidents',
    urgency: 'Varies by percentage',
    why: 'Teams with responders having multiple active incidents face work bottlenecks and burnout.',
    what: 'Percentage of Team responders with more than one active incident.',
    expected_value: '< 75%',
  },
  {
    id: 'team-eps-inactive-users',
    object_type: 'Team',
    rule: 'Team Escalation Policies with Inactive Users %',
    urgency: 'Varies by percentage',
    why: 'Inactive users on Team Escalation Policies can lead to incidents not being created.',
    what: 'Percentage of Team Escalation Policies containing inactive users.',
    expected_value: '0%',
  },
  {
    id: 'team-eps-loops',
    object_type: 'Team',
    rule: 'Team Escalation Policies > 1 Loop %',
    urgency: 'Varies by percentage',
    why: 'Escalation Policies with more than one loop lowers chances of unacknowledged incidents.',
    what: 'Percentage of Team Escalation Policies with more than one loop.',
    expected_value: '> 75%',
  },
  {
    id: 'team-eps-layers',
    object_type: 'Team',
    rule: 'Team Escalation Policies >= 3 Layer %',
    urgency: 'Varies by percentage',
    why: 'Having less than 3 layers increases the risk of missed incidents.',
    what: 'Percentage of Team Escalation Policies with 3 or more layers.',
    expected_value: '> 75%',
  },
  {
    id: 'team-service-active-incidents',
    object_type: 'Team',
    rule: 'Team Service Active Incidents %',
    urgency: 'Varies by percentage',
    why: 'Teams with Services having high active incidents may face increased MTTA and MTTR.',
    what: 'Percentage of Team Services with active incidents at Critical or Major urgency.',
    expected_value: '0%',
  },
  {
    id: 'team-user-oncall-pct',
    object_type: 'Team',
    rule: 'Team User On Call %',
    urgency: 'Varies by percentage',
    why: 'Teams with responders on call for multiple areas increases burnout risk.',
    what: 'Percentage of Team users with excessive on-call assignments.',
    expected_value: '0%',
  },
  {
    id: 'team-eps-gaps',
    object_type: 'Team',
    rule: 'Teams Escalation Policies with Gaps %',
    urgency: 'Critical / Urgent Recommendation',
    why: 'Teams with Escalation Policies having coverage gaps creates critical incident response risks.',
    what: 'Percentage of Team Escalation Policies with time gaps in on-call coverage.',
    expected_value: '0%',
  },

  // SERVICE CHECKS
  {
    id: 'service-transient-incidents',
    object_type: 'Service',
    rule: 'Services should not have Transient Incidents',
    urgency: 'Varies by percentage',
    why: 'Services with high transient incidents lead to decreased productivity, on-call burnout, and alert noise.',
    what: 'Percentage of incidents that are auto-resolved without human action, typically under 10 minutes.',
    expected_value: '< 5%',
  },
  {
    id: 'service-triggered-count',
    object_type: 'Service',
    rule: 'Service Triggered Incident Count',
    urgency: 'Varies by count',
    why: 'High number of triggered incidents can overload Teams, increase MTTA, and cause burnout.',
    what: 'Current number of incidents in Triggered Status for the Service.',
    expected_value: '<= 1',
  },
  {
    id: 'service-active-count',
    object_type: 'Service',
    rule: 'Service Active Incident Count',
    urgency: 'Varies by count',
    why: 'High number of active incidents can overload Teams, increase MTTA/MTTR, and cause burnout.',
    what: 'Current number of incidents in Active Status (Triggered or Acknowledged) for the Service.',
    expected_value: '<= 1',
  },
  {
    id: 'service-acknowledged-count',
    object_type: 'Service',
    rule: 'Service Acknowledged Incident Count',
    urgency: 'Varies by count',
    why: 'High acknowledged incidents can strain Teams, increase MTTR, and affect customer relationships.',
    what: 'Current number of incidents in Acknowledged Status for the Service.',
    expected_value: '<= 1',
  },
  {
    id: 'service-acknowledged-pct',
    object_type: 'Service',
    rule: 'Service Acknowledged Incident %',
    urgency: 'Varies by percentage',
    why: 'High percentage of acknowledged incidents can strain Teams and increase resolution times.',
    what: 'Percentage of acknowledged incidents over last 90 days for the Service.',
    expected_value: '0%',
  },
  {
    id: 'service-active-pct',
    object_type: 'Service',
    rule: 'Service Active Incident %',
    urgency: 'Varies by percentage',
    why: 'High percentage of active incidents can overload Teams and slow resolution.',
    what: 'Percentage of active incidents over last 90 days for the Service.',
    expected_value: '0%',
  },
  {
    id: 'service-triggered-pct',
    object_type: 'Service',
    rule: 'Service Triggered Incident %',
    urgency: 'Varies by percentage',
    why: 'High percentage of triggered incidents can overload Teams and waste resources on non-actionable alerts.',
    what: 'Percentage of triggered incidents over last 90 days for the Service.',
    expected_value: '0%',
  },
];

export function getHealthChecksByObjectType(objectType: string): HealthCheck[] {
  return HEALTH_CHECKS.filter(hc => hc.object_type === objectType);
}

export function getSeverityColor(severity?: string): string {
  switch (severity) {
    case 'critical': return '#e53e3e';
    case 'major': return '#ed8936';
    case 'high': return '#f6ad55';
    case 'medium': return '#4299e1';
    case 'low': return '#48bb78';
    case 'minor': return '#9ae6b4';
    default: return '#a0aec0';
  }
}

export function getStatusEmoji(status?: string): string {
  switch (status) {
    case 'pass': return '✅';
    case 'warning': return '⚠️';
    case 'fail': return '❌';
    default: return '🔍';
  }
}
