// Customer Success Office Hours Management System
// TypeScript implementation for post-incident customer engagement

import { addDays, addWeeks, format, isAfter, isBefore } from 'date-fns';

// Core domain types
interface Customer {
  id: string;
  name: string;
  segment: 'enterprise' | 'business' | 'startup';
  contractValue: number;
  incidentImpact: 'high' | 'medium' | 'low';
  primaryContact: ContactInfo;
  successManager: string;
  lastEngagement?: Date;
  trustScore?: number; // 1-10 scale
}

interface ContactInfo {
  name: string;
  email: string;
  phone?: string;
  role: string;
  timezone: string;
}

interface OfficeHoursSession {
  id: string;
  type: 'emergency' | 'regular' | 'executive' | 'power_user';
  date: Date;
  duration: number; // minutes
  capacity: number;
  facilitators: string[];
  description: string;
  registrations: SessionRegistration[];
  agenda?: string[];
  recordingUrl?: string;
  followUpActions?: FollowUpAction[];
  sentiment?: 'positive' | 'neutral' | 'negative';
  npsScore?: number;
}

interface SessionRegistration {
  customerId: string;
  contactName: string;
  email: string;
  registeredAt: Date;
  attended: boolean;
  questionsSubmitted: string[];
  feedbackSubmitted?: SessionFeedback;
}

interface SessionFeedback {
  rating: number; // 1-5 stars
  helpfulnessScore: number; // 1-10
  comments: string;
  suggestedTopics: string[];
  willAttendFuture: boolean;
}

interface FollowUpAction {
  customerId: string;
  action: string;
  assignedTo: string;
  dueDate: Date;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'high' | 'medium' | 'low';
}

interface ExecutiveOutreach {
  customerId: string;
  executiveName: string;
  executiveRole: string;
  scheduledDate: Date;
  completedDate?: Date;
  duration?: number;
  outcome: string;
  followUpRequired: boolean;
  trustScoreImpact?: number;
}

// Main office hours management class
export class OfficeHoursManager {
  private sessions: Map<string, OfficeHoursSession> = new Map();
  private customers: Map<string, Customer> = new Map();
  private executiveOutreach: Map<string, ExecutiveOutreach[]> = new Map();
  private engagementMetrics: EngagementMetrics;

  constructor() {
    this.engagementMetrics = new EngagementMetrics();
    this.initializePostIncidentProgram();
  }

  // Initialize the post-incident office hours program
  private initializePostIncidentProgram(): void {
    const today = new Date();
    
    // Create emergency office hours for first 2 weeks (daily)
    for (let i = 0; i < 14; i++) {
      const sessionDate = addDays(today, i);
      
      // Morning session
      this.createSession({
        type: 'emergency',
        date: new Date(sessionDate.setHours(10, 0, 0, 0)),
        duration: 30,
        capacity: 50,
        facilitators: ['engineering-lead@company.com', 'customer-success@company.com'],
        description: 'Emergency Office Hours - Addressing Post-Incident Concerns',
        agenda: [
          'Incident update and current status',
          'Prevention measures implemented',
          'Open Q&A session',
          'Individual follow-up scheduling'
        ]
      });
      
      // Evening session for different timezones
      this.createSession({
        type: 'emergency',
        date: new Date(sessionDate.setHours(17, 0, 0, 0)),
        duration: 30,
        capacity: 50,
        facilitators: ['product-manager@company.com', 'customer-success@company.com'],
        description: 'Emergency Office Hours - Evening Session',
        agenda: [
          'Day\'s progress summary',
          'Addressing specific customer concerns',
          'Roadmap transparency session'
        ]
      });
    }
    
    // Schedule regular ongoing sessions
    this.scheduleRegularSessions();
  }

  private scheduleRegularSessions(): void {
    const startDate = addWeeks(new Date(), 2); // Start after emergency period
    
    // Weekly power user sessions
    for (let i = 0; i < 12; i++) { // 3 months worth
      const sessionDate = addWeeks(startDate, i);
      
      this.createSession({
        type: 'power_user',
        date: new Date(sessionDate.setHours(14, 0, 0, 0)), // 2 PM every Wednesday
        duration: 60,
        capacity: 25,
        facilitators: ['senior-engineer@company.com', 'product-specialist@company.com'],
        description: 'Power User Office Hours - Advanced Features & Best Practices',
        agenda: [
          'Advanced feature deep-dive',
          'Customer success story sharing',
          'Beta feature previews',
          'Integration best practices'
        ]
      });
    }
    
    // Monthly executive sessions
    for (let i = 0; i < 6; i++) { // 6 months worth
      const sessionDate = addWeeks(startDate, i * 4);
      
      this.createSession({
        type: 'executive',
        date: new Date(sessionDate.setHours(16, 0, 0, 0)), // 4 PM monthly
        duration: 45,
        capacity: 15,
        facilitators: ['cto@company.com', 'vp-customer-success@company.com'],
        description: 'Executive Office Hours - Strategic Partnership & Roadmap',
        agenda: [
          'Product roadmap updates',
          'Strategic partnership opportunities',
          'Industry trends discussion',
          'Executive feedback collection'
        ]
      });
    }
  }

  // Create a new office hours session
  createSession(sessionData: Omit<OfficeHoursSession, 'id' | 'registrations' | 'followUpActions'>): string {
    const sessionId = this.generateSessionId();
    
    const session: OfficeHoursSession = {
      id: sessionId,
      ...sessionData,
      registrations: [],
      followUpActions: []
    };
    
    this.sessions.set(sessionId, session);
    
    // Auto-invite relevant customers based on session type
    this.autoInviteCustomers(session);
    
    console.log(`Created ${sessionData.type} office hours session for ${format(sessionData.date, 'yyyy-MM-dd HH:mm')}`);
    return sessionId;
  }

  // Auto-invite customers based on session type and customer segment
  private autoInviteCustomers(session: OfficeHoursSession): void {
    const eligibleCustomers = Array.from(this.customers.values()).filter(customer => {
      switch (session.type) {
        case 'emergency':
          return customer.incidentImpact === 'high' || customer.segment === 'enterprise';
        case 'executive':
          return customer.segment === 'enterprise' && customer.contractValue > 100000;
        case 'power_user':
          return customer.lastEngagement && isAfter(customer.lastEngagement, addDays(new Date(), -30));
        default:
          return true;
      }
    });
    
    // Send invitations (in real implementation, this would trigger email/calendar invites)
    eligibleCustomers.forEach(customer => {
      this.sendSessionInvitation(session, customer);
    });
  }

  // Register customer for office hours session
  registerCustomer(sessionId: string, customerId: string, contactEmail: string, questions: string[] = []): boolean {
    const session = this.sessions.get(sessionId);
    const customer = this.customers.get(customerId);
    
    if (!session || !customer) {
      throw new Error('Session or customer not found');
    }
    
    if (session.registrations.length >= session.capacity) {
      return false; // Session full
    }
    
    const registration: SessionRegistration = {
      customerId,
      contactName: customer.primaryContact.name,
      email: contactEmail,
      registeredAt: new Date(),
      attended: false,
      questionsSubmitted: questions
    };
    
    session.registrations.push(registration);
    this.engagementMetrics.recordRegistration(customerId, sessionId, session.type);
    
    console.log(`Registered ${customer.name} for session ${sessionId}`);
    return true;
  }

  // Mark attendance and collect feedback
  markAttendance(sessionId: string, customerId: string, attended: boolean, feedback?: SessionFeedback): void {
    const session = this.sessions.get(sessionId);
    if (!session) return;
    
    const registration = session.registrations.find(r => r.customerId === customerId);
    if (!registration) return;
    
    registration.attended = attended;
    if (feedback) {
      registration.feedbackSubmitted = feedback;
    }
    
    this.engagementMetrics.recordAttendance(customerId, sessionId, attended, feedback?.rating);
    
    // Update customer trust score based on engagement
    if (attended && feedback) {
      this.updateCustomerTrustScore(customerId, feedback.rating);
    }
  }

  // Schedule executive outreach for high-value customers
  scheduleExecutiveOutreach(customerId: string, executiveName: string, executiveRole: string): void {
    const customer = this.customers.get(customerId);
    if (!customer || customer.segment !== 'enterprise') {
      throw new Error('Executive outreach only available for enterprise customers');
    }
    
    const outreach: ExecutiveOutreach = {
      customerId,
      executiveName,
      executiveRole,
      scheduledDate: addDays(new Date(), 3), // Schedule within 3 days
      outcome: '',
      followUpRequired: true
    };
    
    if (!this.executiveOutreach.has(customerId)) {
      this.executiveOutreach.set(customerId, []);
    }
    
    this.executiveOutreach.get(customerId)!.push(outreach);
    
    console.log(`Scheduled executive outreach for ${customer.name} with ${executiveName}`);
  }

  // Complete executive outreach and record outcome
  completeExecutiveOutreach(customerId: string, outcome: string, trustScoreImpact: number): void {
    const outreachList = this.executiveOutreach.get(customerId);
    if (!outreachList || outreachList.length === 0) return;
    
    const latestOutreach = outreachList[outreachList.length - 1];
    latestOutreach.completedDate = new Date();
    latestOutreach.outcome = outcome;
    latestOutreach.trustScoreImpact = trustScoreImpact;
    
    // Update customer trust score
    this.updateCustomerTrustScore(customerId, undefined, trustScoreImpact);
    
    this.engagementMetrics.recordExecutiveOutreach(customerId, trustScoreImpact);
  }

  // Add follow-up action to session
  addFollowUpAction(sessionId: string, action: FollowUpAction): void {
    const session = this.sessions.get(sessionId);
    if (!session) return;
    
    session.followUpActions = session.followUpActions || [];
    session.followUpActions.push(action);
    
    console.log(`Added follow-up action for customer ${action.customerId}: ${action.action}`);
  }

  // Update customer trust score
  private updateCustomerTrustScore(customerId: string, sessionRating?: number, directImpact?: number): void {
    const customer = this.customers.get(customerId);
    if (!customer) return;
    
    const currentScore = customer.trustScore || 5; // Default to neutral
    let newScore = currentScore;
    
    if (sessionRating) {
      // Convert 1-5 rating to trust score impact
      const ratingImpact = (sessionRating - 3) * 0.5; // -1 to +1 scale
      newScore = Math.max(1, Math.min(10, currentScore + ratingImpact));
    }
    
    if (directImpact) {
      newScore = Math.max(1, Math.min(10, newScore + directImpact));
    }
    
    customer.trustScore = newScore;
    customer.lastEngagement = new Date();
    
    console.log(`Updated trust score for ${customer.name}: ${currentScore} → ${newScore}`);
  }

  // Generate engagement report
  generateEngagementReport(startDate: Date, endDate: Date): EngagementReport {
    const sessionsInPeriod = Array.from(this.sessions.values())
      .filter(session => isAfter(session.date, startDate) && isBefore(session.date, endDate));
    
    const totalSessions = sessionsInPeriod.length;
    const totalRegistrations = sessionsInPeriod.reduce((sum, session) => sum + session.registrations.length, 0);
    const totalAttendees = sessionsInPeriod.reduce((sum, session) => 
      sum + session.registrations.filter(r => r.attended).length, 0);
    
    const attendanceRate = totalRegistrations > 0 ? (totalAttendees / totalRegistrations) * 100 : 0;
    
    const feedbackRatings = sessionsInPeriod
      .flatMap(session => session.registrations)
      .map(reg => reg.feedbackSubmitted?.rating)
      .filter(rating => rating !== undefined) as number[];
    
    const averageRating = feedbackRatings.length > 0 
      ? feedbackRatings.reduce((sum, rating) => sum + rating, 0) / feedbackRatings.length 
      : 0;
    
    const customersBySegment = this.getEngagementBySegment(sessionsInPeriod);
    
    return {
      period: { start: startDate, end: endDate },
      totalSessions,
      totalRegistrations,
      totalAttendees,
      attendanceRate,
      averageRating,
      customersBySegment,
      sessionsByType: this.getSessionsByType(sessionsInPeriod),
      trustScoreChanges: this.getTrustScoreChanges(),
      executiveOutreachCount: this.getExecutiveOutreachCount(),
      followUpActionStatus: this.getFollowUpActionStatus(sessionsInPeriod)
    };
  }

  // Helper methods for reporting
  private getEngagementBySegment(sessions: OfficeHoursSession[]): Record<string, any> {
    const segmentStats: Record<string, any> = {
      enterprise: { registrations: 0, attendance: 0 },
      business: { registrations: 0, attendance: 0 },
      startup: { registrations: 0, attendance: 0 }
    };
    
    sessions.forEach(session => {
      session.registrations.forEach(reg => {
        const customer = this.customers.get(reg.customerId);
        if (customer) {
          segmentStats[customer.segment].registrations++;
          if (reg.attended) {
            segmentStats[customer.segment].attendance++;
          }
        }
      });
    });
    
    // Calculate attendance rates
    Object.keys(segmentStats).forEach(segment => {
      const stats = segmentStats[segment];
      stats.attendanceRate = stats.registrations > 0 ? (stats.attendance / stats.registrations) * 100 : 0;
    });
    
    return segmentStats;
  }

  private getSessionsByType(sessions: OfficeHoursSession[]): Record<string, number> {
    return sessions.reduce((acc, session) => {
      acc[session.type] = (acc[session.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
  }

  private getTrustScoreChanges(): { improved: number; declined: number; average: number } {
    const customers = Array.from(this.customers.values());
    const scores = customers.map(c => c.trustScore || 5);
    
    return {
      improved: customers.filter(c => (c.trustScore || 5) > 5).length,
      declined: customers.filter(c => (c.trustScore || 5) < 5).length,
      average: scores.reduce((sum, score) => sum + score, 0) / scores.length
    };
  }

  private getExecutiveOutreachCount(): number {
    return Array.from(this.executiveOutreach.values())
      .reduce((total, outreachList) => total + outreachList.length, 0);
  }

  private getFollowUpActionStatus(sessions: OfficeHoursSession[]): Record<string, number> {
    const allActions = sessions.flatMap(s => s.followUpActions || []);
    
    return {
      pending: allActions.filter(a => a.status === 'pending').length,
      in_progress: allActions.filter(a => a.status === 'in_progress').length,
      completed: allActions.filter(a => a.status === 'completed').length
    };
  }

  // Utility methods
  private generateSessionId(): string {
    return `OH-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private sendSessionInvitation(session: OfficeHoursSession, customer: Customer): void {
    // In real implementation, this would send calendar invites and emails
    console.log(`Sending invitation to ${customer.name} for ${session.type} session on ${format(session.date, 'yyyy-MM-dd HH:mm')}`);
  }

  // Public API methods
  addCustomer(customer: Customer): void {
    this.customers.set(customer.id, customer);
  }

  getSession(sessionId: string): OfficeHoursSession | undefined {
    return this.sessions.get(sessionId);
  }

  getUpcomingSessions(count: number = 10): OfficeHoursSession[] {
    const now = new Date();
    return Array.from(this.sessions.values())
      .filter(session => isAfter(session.date, now))
      .sort((a, b) => a.date.getTime() - b.date.getTime())
      .slice(0, count);
  }

  getCustomerEngagement(customerId: string): CustomerEngagementSummary {
    const customer = this.customers.get(customerId);
    if (!customer) throw new Error('Customer not found');
    
    const registrations = Array.from(this.sessions.values())
      .flatMap(session => session.registrations.filter(r => r.customerId === customerId));
    
    const attended = registrations.filter(r => r.attended).length;
    const avgRating = registrations
      .map(r => r.feedbackSubmitted?.rating)
      .filter(rating => rating !== undefined)
      .reduce((sum, rating, _, arr) => sum + (rating as number) / arr.length, 0);
    
    return {
      customer,
      totalRegistrations: registrations.length,
      totalAttended: attended,
      attendanceRate: registrations.length > 0 ? (attended / registrations.length) * 100 : 0,
      averageRating: avgRating || 0,
      lastEngagement: customer.lastEngagement,
      currentTrustScore: customer.trustScore || 5
    };
  }
}

// Supporting classes and interfaces
class EngagementMetrics {
  private registrations: Map<string, number> = new Map();
  private attendance: Map<string, number> = new Map();
  private ratings: Map<string, number[]> = new Map();

  recordRegistration(customerId: string, sessionId: string, sessionType: string): void {
    const key = `${customerId}-registrations`;
    this.registrations.set(key, (this.registrations.get(key) || 0) + 1);
  }

  recordAttendance(customerId: string, sessionId: string, attended: boolean, rating?: number): void {
    if (attended) {
      const key = `${customerId}-attendance`;
      this.attendance.set(key, (this.attendance.get(key) || 0) + 1);
    }
    
    if (rating) {
      const key = `${customerId}-ratings`;
      const currentRatings = this.ratings.get(key) || [];
      this.ratings.set(key, [...currentRatings, rating]);
    }
  }

  recordExecutiveOutreach(customerId: string, trustScoreImpact: number): void {
    console.log(`Recorded executive outreach for ${customerId} with trust impact: ${trustScoreImpact}`);
  }
}

interface EngagementReport {
  period: { start: Date; end: Date };
  totalSessions: number;
  totalRegistrations: number;
  totalAttendees: number;
  attendanceRate: number;
  averageRating: number;
  customersBySegment: Record<string, any>;
  sessionsByType: Record<string, number>;
  trustScoreChanges: { improved: number; declined: number; average: number };
  executiveOutreachCount: number;
  followUpActionStatus: Record<string, number>;
}

interface CustomerEngagementSummary {
  customer: Customer;
  totalRegistrations: number;
  totalAttended: number;
  attendanceRate: number;
  averageRating: number;
  lastEngagement?: Date;
  currentTrustScore: number;
}

// Example usage and testing
export function demonstrateOfficeHoursProgram(): void {
  const officeHours = new OfficeHoursManager();
  
  // Add sample customers
  const enterpriseCustomer: Customer = {
    id: 'cust-001',
    name: 'TechCorp Enterprise',
    segment: 'enterprise',
    contractValue: 250000,
    incidentImpact: 'high',
    primaryContact: {
      name: 'Sarah Johnson',
      email: 'sarah.johnson@techcorp.com',
      role: 'CTO',
      timezone: 'America/New_York'
    },
    successManager: 'cs-manager@company.com',
    trustScore: 3 // Low due to incident
  };
  
  const businessCustomer: Customer = {
    id: 'cust-002',
    name: 'MidSize Solutions',
    segment: 'business',
    contractValue: 50000,
    incidentImpact: 'medium',
    primaryContact: {
      name: 'Mike Chen',
      email: 'mike.chen@midsize.com',
      role: 'Engineering Manager',
      timezone: 'America/Los_Angeles'
    },
    successManager: 'cs-manager@company.com',
    trustScore: 4
  };
  
  officeHours.addCustomer(enterpriseCustomer);
  officeHours.addCustomer(businessCustomer);
  
  // Schedule executive outreach for enterprise customer
  officeHours.scheduleExecutiveOutreach('cust-001', 'Jane Smith', 'CEO');
  
  // Simulate customer registration and attendance
  const upcomingSessions = officeHours.getUpcomingSessions(5);
  
  if (upcomingSessions.length > 0) {
    const firstSession = upcomingSessions[0];
    
    // Register customers
    officeHours.registerCustomer(firstSession.id, 'cust-001', 'sarah.johnson@techcorp.com', [
      'What specific measures are in place to prevent this incident from recurring?',
      'Can we get dedicated infrastructure for enterprise customers?'
    ]);
    
    officeHours.registerCustomer(firstSession.id, 'cust-002', 'mike.chen@midsize.com', [
      'When will the performance improvements be fully deployed?'
    ]);
    
    // Simulate attendance and feedback
    officeHours.markAttendance(firstSession.id, 'cust-001', true, {
      rating: 4,
      helpfulnessScore: 8,
      comments: 'Great transparency and clear action plan. Appreciated the direct engagement.',
      suggestedTopics: ['Infrastructure scaling', 'Monitoring improvements'],
      willAttendFuture: true
    });
    
    officeHours.markAttendance(firstSession.id, 'cust-002', true, {
      rating: 4,
      helpfulnessScore: 7,
      comments: 'Good session but would like more technical details.',
      suggestedTopics: ['Technical deep-dive sessions'],
      willAttendFuture: true
    });
    
    // Add follow-up actions
    officeHours.addFollowUpAction(firstSession.id, {
      customerId: 'cust-001',
      action: 'Schedule dedicated infrastructure discussion with technical team',
      assignedTo: 'technical-account-manager@company.com',
      dueDate: addDays(new Date(), 7),
      status: 'pending',
      priority: 'high'
    });
  }
  
  // Complete executive outreach
  officeHours.completeExecutiveOutreach('cust-001', 
    'Successful call with CEO. Customer appreciates personal attention and commitment to reliability. Discussed strategic partnership opportunities.',
    2 // Positive trust score impact
  );
  
  // Generate engagement report
  const report = officeHours.generateEngagementReport(
    new Date('2024-01-01'),
    new Date('2024-06-30')
  );
  
  console.log('Office Hours Engagement Report:', JSON.stringify(report, null, 2));
  
  // Get individual customer engagement summary
  const customerEngagement = officeHours.getCustomerEngagement('cust-001');
  console.log('Enterprise Customer Engagement:', JSON.stringify(customerEngagement, null, 2));
}
