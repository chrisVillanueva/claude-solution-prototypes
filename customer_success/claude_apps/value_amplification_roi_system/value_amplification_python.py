# Value Amplification & ROI Demonstration System
# Python implementation for comprehensive customer success value tracking

import json
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
import uuid
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Core Enums
class ValueCategory(Enum):
    COST_SAVINGS = "Direct Cost Savings"
    EFFICIENCY_GAINS = "Operational Efficiency"
    REVENUE_IMPACT = "Revenue Generation"
    RISK_MITIGATION = "Risk Reduction"
    STRATEGIC_VALUE = "Strategic Benefits"

class MilestoneType(Enum):
    QUICK_WIN = ("Quick Win", 30, 60)
    GROWTH_MILESTONE = ("Growth Milestone", 90, 180)
    STRATEGIC_GOAL = ("Strategic Goal", 180, 365)
    
    def __init__(self, display_name: str, min_days: int, max_days: int):
        self.display_name = display_name
        self.min_days = min_days
        self.max_days = max_days

class MilestoneStatus(Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    MISSED = "missed"
    DEFERRED = "deferred"

class AdvocacyLevel(Enum):
    NONE = ("Not Engaged", 0)
    REFERENCE = ("Reference Customer", 1)
    CASE_STUDY = ("Case Study Participant", 2)
    SPEAKER = ("Speaking Engagements", 3)
    CHAMPION = ("Community Champion", 4)
    STRATEGIC_PARTNER = ("Strategic Partner", 5)
    
    def __init__(self, description: str, level: int):
        self.description = description
        self.level = level

class SessionType(Enum):
    MONTHLY_REVIEW = "monthly_review"
    QUARTERLY_SUMMIT = "quarterly_summit"
    EXECUTIVE_BRIEFING = "executive_briefing"
    VALUE_WORKSHOP = "value_workshop"
    ROI_DEEP_DIVE = "roi_deep_dive"

# Core Data Models
@dataclass
class ROIMetric:
    """Represents a measurable ROI metric for value tracking"""
    metric_id: str
    category: ValueCategory
    description: str
    baseline_value: Decimal
    current_value: Decimal
    currency: str
    measured_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_improvement(self) -> Decimal:
        """Calculate absolute improvement from baseline"""
        return self.current_value - self.baseline_value
    
    def calculate_improvement_percentage(self) -> Decimal:
        """Calculate percentage improvement from baseline"""
        if self.baseline_value == 0:
            return Decimal('0')
        improvement = self.calculate_improvement()
        return (improvement / self.baseline_value * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def get_value_impact(self) -> str:
        """Get qualitative assessment of value impact"""
        improvement_pct = self.calculate_improvement_percentage()
        if improvement_pct >= 50:
            return "Exceptional"
        elif improvement_pct >= 25:
            return "Significant"
        elif improvement_pct >= 10:
            return "Moderate"
        elif improvement_pct > 0:
            return "Minimal"
        else:
            return "Negative"

@dataclass
class SuccessMilestone:
    """Represents a customer success milestone with tracking capabilities"""
    milestone_id: str
    customer_id: str
    title: str
    description: str
    milestone_type: MilestoneType
    target_date: date
    assigned_owner: str
    status: MilestoneStatus = MilestoneStatus.PLANNED
    achieved_date: Optional[date] = None
    success_criteria: List[str] = field(default_factory=list)
    achievement_metrics: Dict[str, Any] = field(default_factory=dict)
    celebration_plan: str = ""
    stakeholders: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def mark_achieved(self, achieved_date: date, metrics: Dict[str, Any]) -> None:
        """Mark milestone as achieved with metrics"""
        self.status = MilestoneStatus.ACHIEVED
        self.achieved_date = achieved_date
        self.achievement_metrics.update(metrics)
        
    def add_success_criterion(self, criterion: str) -> None:
        """Add a success criterion to the milestone"""
        self.success_criteria.append(criterion)
        
    def add_stakeholder(self, stakeholder: str) -> None:
        """Add a stakeholder to the milestone"""
        if stakeholder not in self.stakeholders:
            self.stakeholders.append(stakeholder)
    
    def is_on_track(self) -> bool:
        """Check if milestone is on track based on target date"""
        today = date.today()
        return today <= self.target_date or self.status == MilestoneStatus.ACHIEVED
    
    def days_until_due(self) -> int:
        """Calculate days until milestone is due"""
        return (self.target_date - date.today()).days
    
    def is_overdue(self) -> bool:
        """Check if milestone is overdue"""
        return date.today() > self.target_date and self.status not in [MilestoneStatus.ACHIEVED, MilestoneStatus.DEFERRED]

@dataclass
class ValueDemonstrationSession:
    """Represents a value demonstration session with customers"""
    session_id: str
    customer_id: str
    session_type: SessionType
    scheduled_date: datetime
    duration_minutes: int
    facilitator: str
    attendees: List[str] = field(default_factory=list)
    agenda: List[str] = field(default_factory=list)
    presented_metrics: Dict[str, str] = field(default_factory=dict)  # metric_id -> presentation_notes
    key_outcomes: List[str] = field(default_factory=list)
    follow_up_actions: List[str] = field(default_factory=list)
    completed: bool = False
    satisfaction_rating: int = 0  # 1-10 scale
    session_notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_attendee(self, attendee: str) -> None:
        """Add an attendee to the session"""
        if attendee not in self.attendees:
            self.attendees.append(attendee)
    
    def add_agenda_item(self, item: str) -> None:
        """Add an agenda item"""
        self.agenda.append(item)
    
    def add_presented_metric(self, metric_id: str, notes: str = "") -> None:
        """Add a metric that was presented in the session"""
        self.presented_metrics[metric_id] = notes
    
    def complete_session(self, satisfaction_rating: int, session_notes: str, 
                        key_outcomes: List[str], follow_up_actions: List[str]) -> None:
        """Mark session as completed with results"""
        self.completed = True
        self.satisfaction_rating = satisfaction_rating
        self.session_notes = session_notes
        self.key_outcomes.extend(key_outcomes)
        self.follow_up_actions.extend(follow_up_actions)

@dataclass
class CustomerAdvocacyProfile:
    """Tracks customer advocacy engagement and progression"""
    customer_id: str
    current_level: AdvocacyLevel = AdvocacyLevel.NONE
    enrolled_date: datetime = field(default_factory=datetime.now)
    advocacy_coordinator: str = ""
    willing_to_participate: bool = False
    participated_activities: List[str] = field(default_factory=list)
    contribution_metrics: Dict[str, Any] = field(default_factory=dict)
    recognition_received: List[str] = field(default_factory=list)
    expertise_areas: List[str] = field(default_factory=list)
    preferences: Dict[str, str] = field(default_factory=dict)
    
    def promote_advocacy_level(self, new_level: AdvocacyLevel, reason: str) -> bool:
        """Promote customer to a higher advocacy level"""
        if new_level.level > self.current_level.level:
            old_level = self.current_level
            self.current_level = new_level
            activity = f"Promoted from {old_level.description} to {new_level.description}: {reason}"
            self.participated_activities.append(activity)
            return True
        return False
    
    def add_activity(self, activity: str, metrics: Optional[Dict[str, Any]] = None) -> None:
        """Add an advocacy activity"""
        self.participated_activities.append(f"{datetime.now().strftime('%Y-%m-%d')}: {activity}")
        if metrics:
            self.contribution_metrics.update(metrics)
    
    def add_recognition(self, recognition: str) -> None:
        """Add recognition received"""
        self.recognition_received.append(f"{datetime.now().strftime('%Y-%m-%d')}: {recognition}")
    
    def add_expertise_area(self, area: str) -> None:
        """Add area of expertise"""
        if area not in self.expertise_areas:
            self.expertise_areas.append(area)

# Core Value Amplification Engine
class ValueAmplificationEngine:
    """Main engine for managing customer value amplification and ROI demonstration"""
    
    def __init__(self):
        self.customers_roi_metrics: Dict[str, Dict[str, ROIMetric]] = defaultdict(dict)
        self.customer_milestones: Dict[str, List[SuccessMilestone]] = defaultdict(list)
        self.customer_sessions: Dict[str, List[ValueDemonstrationSession]] = defaultdict(list)
        self.advocacy_profiles: Dict[str, CustomerAdvocacyProfile] = {}
        self.notification_service = NotificationService()
        
    # ROI Tracking Methods
    def add_roi_metric(self, customer_id: str, metric: ROIMetric) -> None:
        """Add a new ROI metric for a customer"""
        self.customers_roi_metrics[customer_id][metric.metric_id] = metric
        
        logger.info(f"Added ROI metric for customer {customer_id}: {metric.description} = "
                   f"{metric.current_value} {metric.currency} "
                   f"({metric.calculate_improvement_percentage()}% improvement)")
        
        # Check for milestone completion triggers
        self._check_milestone_completion_triggers(customer_id, metric)
        
        # Send notifications for significant improvements
        if metric.calculate_improvement_percentage() >= 25:
            self.notification_service.send_roi_improvement_alert(customer_id, metric)
    
    def update_roi_metric(self, customer_id: str, metric_id: str, new_value: Decimal, 
                         additional_metadata: Optional[Dict[str, Any]] = None) -> Optional[ROIMetric]:
        """Update an existing ROI metric"""
        customer_metrics = self.customers_roi_metrics.get(customer_id)
        if not customer_metrics or metric_id not in customer_metrics:
            logger.warning(f"ROI metric {metric_id} not found for customer {customer_id}")
            return None
        
        existing_metric = customer_metrics[metric_id]
        
        # Create updated metric
        updated_metric = ROIMetric(
            metric_id=existing_metric.metric_id,
            category=existing_metric.category,
            description=existing_metric.description,
            baseline_value=existing_metric.baseline_value,
            current_value=new_value,
            currency=existing_metric.currency,
            measured_at=datetime.now(),
            metadata=existing_metric.metadata.copy()
        )
        
        if additional_metadata:
            updated_metric.metadata.update(additional_metadata)
        
        customer_metrics[metric_id] = updated_metric
        
        improvement = updated_metric.calculate_improvement_percentage()
        logger.info(f"Updated ROI metric for customer {customer_id}: {updated_metric.description} "
                   f"improved by {improvement}%")
        
        return updated_metric
    
    def calculate_total_roi(self, customer_id: str) -> Decimal:
        """Calculate total ROI across all metrics for a customer"""
        customer_metrics = self.customers_roi_metrics.get(customer_id, {})
        if not customer_metrics:
            return Decimal('0')
        
        total_baseline = sum(metric.baseline_value for metric in customer_metrics.values())
        total_current = sum(metric.current_value for metric in customer_metrics.values())
        
        if total_baseline == 0:
            return Decimal('0')
        
        return ((total_current - total_baseline) / total_baseline * 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def get_roi_by_category(self, customer_id: str) -> Dict[ValueCategory, Decimal]:
        """Get ROI breakdown by value category"""
        customer_metrics = self.customers_roi_metrics.get(customer_id, {})
        category_roi = {}
        
        for category in ValueCategory:
            category_metrics = [m for m in customer_metrics.values() if m.category == category]
            if category_metrics:
                total_baseline = sum(metric.baseline_value for metric in category_metrics)
                total_current = sum(metric.current_value for metric in category_metrics)
                
                if total_baseline > 0:
                    roi = ((total_current - total_baseline) / total_baseline * 100).quantize(
                        Decimal('0.01'), rounding=ROUND_HALF_UP)
                    category_roi[category] = roi
                else:
                    category_roi[category] = Decimal('0')
            else:
                category_roi[category] = Decimal('0')
        
        return category_roi
    
    # Milestone Management Methods
    def create_success_milestone(self, customer_id: str, title: str, description: str,
                               milestone_type: MilestoneType, target_date: date, 
                               assigned_owner: str) -> str:
        """Create a new success milestone for a customer"""
        milestone_id = f"MILESTONE-{customer_id}-{milestone_type.name}-{uuid.uuid4().hex[:8]}"
        
        milestone = SuccessMilestone(
            milestone_id=milestone_id,
            customer_id=customer_id,
            title=title,
            description=description,
            milestone_type=milestone_type,
            target_date=target_date,
            assigned_owner=assigned_owner
        )
        
        self.customer_milestones[customer_id].append(milestone)
        
        logger.info(f"Created {milestone_type.display_name} milestone for customer {customer_id}: {title}")
        
        # Schedule milestone reminders
        self._schedule_milestone_reminders(milestone)
        
        return milestone_id
    
    def achieve_milestone(self, customer_id: str, milestone_id: str, 
                         achievement_metrics: Dict[str, Any], celebration_plan: str = "") -> bool:
        """Mark a milestone as achieved"""
        milestones = self.customer_milestones.get(customer_id, [])
        
        for milestone in milestones:
            if milestone.milestone_id == milestone_id:
                milestone.mark_achieved(date.today(), achievement_metrics)
                milestone.celebration_plan = celebration_plan
                
                logger.info(f"Milestone achieved for customer {customer_id}: {milestone.title}")
                
                # Trigger celebration activities
                self._trigger_milestone_celebration(milestone)
                
                # Check for advocacy level promotion
                self._check_advocacy_level_promotion(customer_id, milestone)
                
                return True
        
        logger.warning(f"Milestone {milestone_id} not found for customer {customer_id}")
        return False
    
    def get_upcoming_milestones(self, customer_id: str, days_ahead: int = 30) -> List[SuccessMilestone]:
        """Get upcoming milestones for a customer"""
        milestones = self.customer_milestones.get(customer_id, [])
        cutoff_date = date.today() + timedelta(days=days_ahead)
        
        upcoming = [
            milestone for milestone in milestones
            if milestone.status in [MilestoneStatus.PLANNED, MilestoneStatus.IN_PROGRESS]
            and milestone.target_date <= cutoff_date
        ]
        
        return sorted(upcoming, key=lambda m: m.target_date)
    
    def get_overdue_milestones(self, customer_id: str) -> List[SuccessMilestone]:
        """Get overdue milestones for a customer"""
        milestones = self.customer_milestones.get(customer_id, [])
        return [milestone for milestone in milestones if milestone.is_overdue()]
    
    # Value Demonstration Session Methods
    def schedule_value_demonstration_session(self, customer_id: str, session_type: SessionType,
                                           scheduled_date: datetime, duration_minutes: int, 
                                           facilitator: str) -> str:
        """Schedule a value demonstration session"""
        session_id = f"SESSION-{customer_id}-{session_type.value}-{uuid.uuid4().hex[:8]}"
        
        session = ValueDemonstrationSession(
            session_id=session_id,
            customer_id=customer_id,
            session_type=session_type,
            scheduled_date=scheduled_date,
            duration_minutes=duration_minutes,
            facilitator=facilitator
        )
        
        # Pre-populate with relevant ROI metrics
        customer_metrics = self.customers_roi_metrics.get(customer_id, {})
        for metric_id in customer_metrics.keys():
            session.add_presented_metric(metric_id, "Included in session dashboard")
        
        self.customer_sessions[customer_id].append(session)
        
        logger.info(f"Scheduled {session_type.value} session for customer {customer_id} on "
                   f"{scheduled_date.strftime('%Y-%m-%d %H:%M')}")
        
        return session_id
    
    def complete_value_demonstration_session(self, customer_id: str, session_id: str,
                                           satisfaction_rating: int, session_notes: str,
                                           key_outcomes: List[str], follow_up_actions: List[str]) -> bool:
        """Complete a value demonstration session with results"""
        sessions = self.customer_sessions.get(customer_id, [])
        
        for session in sessions:
            if session.session_id == session_id:
                session.complete_session(satisfaction_rating, session_notes, key_outcomes, follow_up_actions)
                
                logger.info(f"Completed value demonstration session for customer {customer_id}: "
                           f"rating {satisfaction_rating}/10")
                
                # Analyze session effectiveness
                self._analyze_session_effectiveness(session)
                
                return True
        
        logger.warning(f"Session {session_id} not found for customer {customer_id}")
        return False
    
    def get_session_history(self, customer_id: str, limit: int = 10) -> List[ValueDemonstrationSession]:
        """Get recent session history for a customer"""
        sessions = self.customer_sessions.get(customer_id, [])
        completed_sessions = [s for s in sessions if s.completed]
        return sorted(completed_sessions, key=lambda s: s.scheduled_date, reverse=True)[:limit]
    
    # Advocacy Program Methods
    def enroll_in_advocacy_program(self, customer_id: str, advocacy_coordinator: str) -> None:
        """Enroll a customer in the advocacy program"""
        profile = CustomerAdvocacyProfile(
            customer_id=customer_id,
            advocacy_coordinator=advocacy_coordinator,
            willing_to_participate=True
        )
        
        self.advocacy_profiles[customer_id] = profile
        
        logger.info(f"Enrolled customer {customer_id} in advocacy program with coordinator {advocacy_coordinator}")
    
    def record_advocacy_activity(self, customer_id: str, activity: str, 
                                contribution_metrics: Optional[Dict[str, Any]] = None) -> None:
        """Record an advocacy activity for a customer"""
        profile = self.advocacy_profiles.get(customer_id)
        if not profile:
            logger.warning(f"Customer {customer_id} not enrolled in advocacy program")
            return
        
        profile.add_activity(activity, contribution_metrics)
        
        logger.info(f"Recorded advocacy activity for customer {customer_id}: {activity}")
        
        # Check for level promotion based on activity
        self._evaluate_advocacy_level_promotion(profile, activity)
    
    def add_advocacy_recognition(self, customer_id: str, recognition: str) -> None:
        """Add recognition for a customer's advocacy contributions"""
        profile = self.advocacy_profiles.get(customer_id)
        if profile:
            profile.add_recognition(recognition)
            logger.info(f"Added recognition for customer {customer_id}: {recognition}")
    
    def get_advocacy_candidates(self, min_satisfaction_rating: int = 8, 
                               min_roi_improvement: Decimal = Decimal('20')) -> List[str]:
        """Get customers who are good candidates for advocacy program enrollment"""
        candidates = []
        
        for customer_id in self.customers_roi_metrics.keys():
            # Skip if already enrolled
            if customer_id in self.advocacy_profiles:
                continue
            
            # Check ROI improvement
            total_roi = self.calculate_total_roi(customer_id)
            if total_roi < min_roi_improvement:
                continue
            
            # Check session satisfaction
            sessions = self.customer_sessions.get(customer_id, [])
            completed_sessions = [s for s in sessions if s.completed and s.satisfaction_rating > 0]
            
            if completed_sessions:
                avg_satisfaction = sum(s.satisfaction_rating for s in completed_sessions) / len(completed_sessions)
                if avg_satisfaction >= min_satisfaction_rating:
                    candidates.append(customer_id)
        
        return candidates
    
    # Analytics and Reporting Methods
    def generate_value_report(self, customer_id: str, start_date: Optional[date] = None, 
                            end_date: Optional[date] = None) -> 'ValueAmplificationReport':
        """Generate comprehensive value report for a customer"""
        if start_date is None:
            start_date = date.today() - timedelta(days=365)
        if end_date is None:
            end_date = date.today()
        
        # Gather data
        roi_metrics = self.customers_roi_metrics.get(customer_id, {})
        milestones = self.customer_milestones.get(customer_id, [])
        sessions = self.customer_sessions.get(customer_id, [])
        advocacy_profile = self.advocacy_profiles.get(customer_id)
        
        # Filter by date range
        relevant_sessions = [
            s for s in sessions 
            if start_date <= s.scheduled_date.date() <= end_date
        ]
        
        relevant_milestones = [
            m for m in milestones
            if (m.achieved_date and start_date <= m.achieved_date <= end_date) or
               (start_date <= m.target_date <= end_date)
        ]
        
        return ValueAmplificationReport(
            customer_id=customer_id,
            report_start_date=start_date,
            report_end_date=end_date,
            total_roi=self.calculate_total_roi(customer_id),
            roi_by_category=self.get_roi_by_category(customer_id),
            roi_metrics=roi_metrics,
            milestones=relevant_milestones,
            sessions=relevant_sessions,
            advocacy_profile=advocacy_profile
        )
    
    def generate_portfolio_report(self, customer_ids: List[str]) -> 'PortfolioValueReport':
        """Generate portfolio-level value report"""
        reports = [self.generate_value_report(customer_id) for customer_id in customer_ids]
        return PortfolioValueReport(reports)
    
    def export_customer_data(self, customer_id: str, format: str = 'json') -> str:
        """Export all customer data in specified format"""
        data = {
            'customer_id': customer_id,
            'roi_metrics': {k: asdict(v) for k, v in self.customers_roi_metrics.get(customer_id, {}).items()},
            'milestones': [asdict(m) for m in self.customer_milestones.get(customer_id, [])],
            'sessions': [asdict(s) for s in self.customer_sessions.get(customer_id, [])],
            'advocacy_profile': asdict(self.advocacy_profiles[customer_id]) if customer_id in self.advocacy_profiles else None,
            'exported_at': datetime.now().isoformat()
        }
        
        if format.lower() == 'json':
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    # Private Helper Methods
    def _check_milestone_completion_triggers(self, customer_id: str, metric: ROIMetric) -> None:
        """Check if ROI improvement triggers any milestone completions"""
        milestones = self.customer_milestones.get(customer_id, [])
        
        for milestone in milestones:
            if milestone.status == MilestoneStatus.IN_PROGRESS:
                if self._does_metric_complete_milestone(metric, milestone):
                    achievement_metrics = {
                        'triggering_metric': metric.metric_id,
                        'improvement_percentage': float(metric.calculate_improvement_percentage()),
                        'auto_completed': True
                    }
                    
                    self.achieve_milestone(customer_id, milestone.milestone_id, achievement_metrics)
    
    def _does_metric_complete_milestone(self, metric: ROIMetric, milestone: SuccessMilestone) -> bool:
        """Check if a metric improvement completes a milestone"""
        improvement_threshold = {
            MilestoneType.QUICK_WIN: Decimal('10'),      # 10% improvement
            MilestoneType.GROWTH_MILESTONE: Decimal('25'), # 25% improvement
            MilestoneType.STRATEGIC_GOAL: Decimal('50')   # 50% improvement
        }
        
        threshold = improvement_threshold.get(milestone.milestone_type, Decimal('10'))
        return metric.calculate_improvement_percentage() >= threshold
    
    def _trigger_milestone_celebration(self, milestone: SuccessMilestone) -> None:
        """Trigger celebration activities for achieved milestone"""
        self.notification_service.send_milestone_celebration_notification(milestone)
        
        if milestone.milestone_type == MilestoneType.STRATEGIC_GOAL:
            logger.info(f"Triggering major celebration for strategic milestone: {milestone.title}")
    
    def _check_advocacy_level_promotion(self, customer_id: str, milestone: SuccessMilestone) -> None:
        """Check if milestone achievement warrants advocacy level promotion"""
        profile = self.advocacy_profiles.get(customer_id)
        if profile and milestone.milestone_type == MilestoneType.STRATEGIC_GOAL:
            if profile.current_level.level < AdvocacyLevel.REFERENCE.level:
                profile.promote_advocacy_level(
                    AdvocacyLevel.REFERENCE, 
                    f"Strategic milestone achievement: {milestone.title}"
                )
    
    def _analyze_session_effectiveness(self, session: ValueDemonstrationSession) -> None:
        """Analyze effectiveness of completed session"""
        if session.satisfaction_rating >= 8:
            logger.info(f"High-satisfaction value session completed: {session.session_id}")
            
            # High satisfaction may indicate advocacy readiness
            if session.customer_id not in self.advocacy_profiles:
                self.notification_service.send_advocacy_enrollment_suggestion(session.customer_id)
    
    def _evaluate_advocacy_level_promotion(self, profile: CustomerAdvocacyProfile, activity: str) -> None:
        """Evaluate if activity warrants advocacy level promotion"""
        current_level = profile.current_level
        new_level = current_level
        
        # Simple promotion logic based on activity type
        activity_lower = activity.lower()
        
        if 'case study' in activity_lower and current_level.level < AdvocacyLevel.CASE_STUDY.level:
            new_level = AdvocacyLevel.CASE_STUDY
        elif 'speaking' in activity_lower and current_level.level < AdvocacyLevel.SPEAKER.level:
            new_level = AdvocacyLevel.SPEAKER
        elif 'champion' in activity_lower and current_level.level < AdvocacyLevel.CHAMPION.level:
            new_level = AdvocacyLevel.CHAMPION
        
        if new_level != current_level:
            profile.promote_advocacy_level(new_level, f"Activity-based promotion: {activity}")
    
    def _schedule_milestone_reminders(self, milestone: SuccessMilestone) -> None:
        """Schedule reminder notifications for milestone"""
        reminder_date = milestone.target_date - timedelta(days=7)  # 1 week before
        
        if reminder_date > date.today():
            logger.info(f"Scheduled reminder for milestone {milestone.title} on {reminder_date}")

# Value Calculation and Analytics Classes
class ValueCalculationService:
    """Service for advanced value calculations and analytics"""
    
    @staticmethod
    def calculate_composite_roi(metrics: List[ROIMetric]) -> Decimal:
        """Calculate composite ROI across multiple metrics"""
        if not metrics:
            return Decimal('0')
        
        total_baseline = sum(metric.baseline_value for metric in metrics)
        total_current = sum(metric.current_value for metric in metrics)
        
        if total_baseline == 0:
            return Decimal('0')
        
        return ((total_current - total_baseline) / total_baseline * 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_roi_trend(metrics_history: List[Tuple[datetime, Decimal]]) -> str:
        """Calculate ROI trend from historical data"""
        if len(metrics_history) < 2:
            return "Insufficient data"
        
        # Sort by date
        sorted_history = sorted(metrics_history, key=lambda x: x[0])
        
        # Calculate trend using linear regression
        x_values = [(dt - sorted_history[0][0]).days for dt, _ in sorted_history]
        y_values = [float(value) for _, value in sorted_history]
        
        if len(x_values) > 1:
            slope = np.polyfit(x_values, y_values, 1)[0]
            
            if slope > 0.1:
                return "Strongly Positive"
            elif slope > 0:
                return "Positive"
            elif slope > -0.1:
                return "Stable"
            else:
                return "Declining"
        
        return "Stable"
    
    @staticmethod
    def calculate_value_velocity(milestones: List[SuccessMilestone]) -> Dict[str, Any]:
        """Calculate velocity of value achievement"""
        achieved_milestones = [m for m in milestones if m.status == MilestoneStatus.ACHIEVED]
        
        if not achieved_milestones:
            return {"velocity": 0, "average_time_to_achievement": 0}
        
        time_to_achievements = []
        for milestone in achieved_milestones:
            if milestone.achieved_date and milestone.created_at:
                days_to_achievement = (milestone.achieved_date - milestone.created_at.date()).days
                time_to_achievements.append(days_to_achievement)
        
        if time_to_achievements:
            avg_time = sum(time_to_achievements) / len(time_to_achievements)
            velocity = len(achieved_milestones) / max(1, avg_time / 30)  # milestones per month
        else:
            avg_time = 0
            velocity = 0
        
        return {
            "velocity": round(velocity, 2),
            "average_time_to_achievement": round(avg_time, 1),
            "total_achieved": len(achieved_milestones)
        }

# Notification Service
class NotificationService:
    """Service for handling notifications and alerts"""
    
    def send_roi_improvement_alert(self, customer_id: str, metric: ROIMetric) -> None:
        """Send alert for significant ROI improvement"""
        logger.info(f"🎉 ROI Improvement Alert: Customer {customer_id} achieved "
                   f"{metric.calculate_improvement_percentage()}% improvement in {metric.description}")
    
    def send_milestone_celebration_notification(self, milestone: SuccessMilestone) -> None:
        """Send milestone celebration notification"""
        logger.info(f"🏆 Milestone Celebration: {milestone.title} achieved for customer {milestone.customer_id}")
    
    def send_advocacy_enrollment_suggestion(self, customer_id: str) -> None:
        """Send suggestion to enroll customer in advocacy program"""
        logger.info(f"💡 Advocacy Suggestion: Customer {customer_id} may be ready for advocacy program enrollment")
    
    def send_milestone_reminder_notification(self, milestone: SuccessMilestone, days_until_due: int) -> None:
        """Send milestone reminder notification"""
        logger.info(f"⏰ Milestone Reminder: {milestone.title} due in {days_until_due} days")

# Reporting Classes
@dataclass
class ValueAmplificationReport:
    """Comprehensive value amplification report for a single customer"""
    customer_id: str
    report_start_date: date
    report_end_date: date
    total_roi: Decimal
    roi_by_category: Dict[ValueCategory, Decimal]
    roi_metrics: Dict[str, ROIMetric]
    milestones: List[SuccessMilestone]
    sessions: List[ValueDemonstrationSession]
    advocacy_profile: Optional[CustomerAdvocacyProfile]
    generated_at: datetime = field(default_factory=datetime.now)
    
    def generate_summary(self) -> 'ValueSummary':
        """Generate executive summary of value amplification"""
        achieved_milestones = len([m for m in self.milestones if m.status == MilestoneStatus.ACHIEVED])
        total_milestones = len(self.milestones)
        
        completed_sessions = [s for s in self.sessions if s.completed]
        avg_session_satisfaction = (
            sum(s.satisfaction_rating for s in completed_sessions) / len(completed_sessions)
            if completed_sessions else 0
        )
        
        advocacy_level = self.advocacy_profile.current_level if self.advocacy_profile else AdvocacyLevel.NONE
        
        return ValueSummary(
            total_roi=self.total_roi,
            achieved_milestones=achieved_milestones,
            total_milestones=total_milestones,
            average_session_satisfaction=avg_session_satisfaction,
            advocacy_level=advocacy_level,
            active_roi_metrics=len(self.roi_metrics),
            report_period_days=(self.report_end_date - self.report_start_date).days
        )
    
    def get_top_performing_metrics(self, limit: int = 5) -> List[ROIMetric]:
        """Get top performing ROI metrics by improvement percentage"""
        metrics_list = list(self.roi_metrics.values())
        return sorted(metrics_list, 
                     key=lambda m: m.calculate_improvement_percentage(), 
                     reverse=True)[:limit]
    
    def generate_visualization_data(self) -> Dict[str, Any]:
        """Generate data for value visualization dashboards"""
        # ROI by category
        category_data = {cat.value: float(roi) for cat, roi in self.roi_by_category.items()}
        
        # Milestone progress
        milestone_status_counts = Counter(m.status.value for m in self.milestones)
        
        # Session satisfaction trend
        session_data = [(s.scheduled_date.date(), s.satisfaction_rating) 
                       for s in self.sessions if s.completed]
        
        return {
            'roi_by_category': category_data,
            'milestone_status': dict(milestone_status_counts),
            'session_satisfaction_trend': session_data,
            'total_roi': float(self.total_roi),
            'advocacy_level': self.advocacy_profile.current_level.description if self.advocacy_profile else "None"
        }

@dataclass
class ValueSummary:
    """Executive summary of value amplification results"""
    total_roi: Decimal
    achieved_milestones: int
    total_milestones: int
    average_session_satisfaction: float
    advocacy_level: AdvocacyLevel
    active_roi_metrics: int
    report_period_days: int
    
    @property
    def milestone_achievement_rate(self) -> float:
        """Calculate milestone achievement rate as percentage"""
        return (self.achieved_milestones / self.total_milestones * 100) if self.total_milestones > 0 else 0
    
    @property
    def roi_impact_level(self) -> str:
        """Get qualitative ROI impact assessment"""
        if self.total_roi >= 50:
            return "Exceptional"
        elif self.total_roi >= 25:
            return "Significant"
        elif self.total_roi >= 10:
            return "Moderate"
        elif self.total_roi > 0:
            return "Minimal"
        else:
            return "Negative"

@dataclass
class PortfolioValueReport:
    """Portfolio-level value amplification report"""
    customer_reports: List[ValueAmplificationReport]
    generated_at: datetime = field(default_factory=datetime.now)
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio-level summary statistics"""
        if not self.customer_reports:
            return {}
        
        total_customers = len(self.customer_reports)
        avg_roi = sum(report.total_roi for report in self.customer_reports) / total_customers
        
        total_milestones = sum(len(report.milestones) for report in self.customer_reports)
        total_achieved = sum(len([m for m in report.milestones if m.status == MilestoneStatus.ACHIEVED]) 
                           for report in self.customer_reports)
        
        advocacy_distribution = Counter(
            report.advocacy_profile.current_level.description if report.advocacy_profile else "None"
            for report in self.customer_reports
        )
        
        return {
            'total_customers': total_customers,
            'average_roi': float(avg_roi),
            'portfolio_milestone_achievement_rate': (total_achieved / total_milestones * 100) if total_milestones > 0 else 0,
            'advocacy_distribution': dict(advocacy_distribution),
            'top_performing_customers': self.get_top_performers(5)
        }
    
    def get_top_performers(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing customers by ROI"""
        sorted_reports = sorted(self.customer_reports, key=lambda r: r.total_roi, reverse=True)
        
        return [
            {
                'customer_id': report.customer_id,
                'total_roi': float(report.total_roi),
                'achieved_milestones': len([m for m in report.milestones if m.status == MilestoneStatus.ACHIEVED]),
                'advocacy_level': report.advocacy_profile.current_level.description if report.advocacy_profile else "None"
            }
            for report in sorted_reports[:limit]
        ]

# Demo and Example Usage
def demonstrate_value_amplification_system():
    """Comprehensive demonstration of the value amplification system"""
    
    logger.info("=== Starting Value Amplification System Demonstration ===")
    
    # Initialize the system
    engine = ValueAmplificationEngine()
    
    # Customer setup
    customer_id = "ENTERPRISE-001"
    
    # 1. Add ROI Metrics
    logger.info("📊 Adding ROI metrics...")
    
    cost_savings_metric = ROIMetric(
        metric_id="COST-001",
        category=ValueCategory.COST_SAVINGS,
        description="Labor Cost Reduction through Automation",
        baseline_value=Decimal('100000'),
        current_value=Decimal('125000'),
        currency="USD"
    )
    cost_savings_metric.metadata.update({
        'department': 'Operations',
        'measurement_period': 'Q1 2024',
        'automation_tools': ['workflow_engine', 'data_processor']
    })
    
    efficiency_metric = ROIMetric(
        metric_id="EFF-001",
        category=ValueCategory.EFFICIENCY_GAINS,
        description="Process Automation Time Savings",
        baseline_value=Decimal('50000'),
        current_value=Decimal('80000'),
        currency="USD"
    )
    
    revenue_metric = ROIMetric(
        metric_id="REV-001",
        category=ValueCategory.REVENUE_IMPACT,
        description="New Revenue from Digital Transformation",
        baseline_value=Decimal('200000'),
        current_value=Decimal('275000'),
        currency="USD"
    )
    
    engine.add_roi_metric(customer_id, cost_savings_metric)
    engine.add_roi_metric(customer_id, efficiency_metric)
    engine.add_roi_metric(customer_id, revenue_metric)
    
    # 2. Create Success Milestones
    logger.info("🎯 Creating success milestones...")
    
    quick_win_id = engine.create_success_milestone(
        customer_id=customer_id,
        title="Initial Workflow Automation",
        description="Automate first critical business process",
        milestone_type=MilestoneType.QUICK_WIN,
        target_date=date.today() + timedelta(days=45),
        assigned_owner="success-manager@company.com"
    )
    
    growth_milestone_id = engine.create_success_milestone(
        customer_id=customer_id,
        title="Department-Wide Adoption",
        description="Expand automation to entire operations department",
        milestone_type=MilestoneType.GROWTH_MILESTONE,
        target_date=date.today() + timedelta(days=120),
        assigned_owner="success-manager@company.com"
    )
    
    strategic_goal_id = engine.create_success_milestone(
        customer_id=customer_id,
        title="Digital Transformation Leadership",
        description="Become industry leader in digital transformation",
        milestone_type=MilestoneType.STRATEGIC_GOAL,
        target_date=date.today() + timedelta(days=300),
        assigned_owner="executive-team@company.com"
    )
    
    # 3. Schedule Value Demonstration Sessions
    logger.info("📅 Scheduling value demonstration sessions...")
    
    monthly_review_id = engine.schedule_value_demonstration_session(
        customer_id=customer_id,
        session_type=SessionType.MONTHLY_REVIEW,
        scheduled_date=datetime.now() + timedelta(days=7),
        duration_minutes=60,
        facilitator="senior-csm@company.com"
    )
    
    quarterly_summit_id = engine.schedule_value_demonstration_session(
        customer_id=customer_id,
        session_type=SessionType.QUARTERLY_SUMMIT,
        scheduled_date=datetime.now() + timedelta(days=30),
        duration_minutes=120,
        facilitator="executive-team@company.com"
    )
    
    # 4. Simulate achieving a milestone
    logger.info("🏆 Simulating milestone achievement...")
    
    achievement_metrics = {
        'processes_automated': 5,
        'time_saved_hours_per_week': 40,
        'user_satisfaction_score': 9.2,
        'roi_improvement': float(cost_savings_metric.calculate_improvement_percentage())
    }
    
    engine.achieve_milestone(customer_id, quick_win_id, achievement_metrics, 
                           "Team celebration lunch and recognition in company newsletter")
    
    # 5. Complete a value demonstration session
    logger.info("✅ Completing value demonstration session...")
    
    engine.complete_value_demonstration_session(
        customer_id=customer_id,
        session_id=monthly_review_id,
        satisfaction_rating=9,
        session_notes="Excellent engagement from customer team. Clear understanding of value delivered.",
        key_outcomes=[
            "Customer committed to expanding usage to 2 additional departments",
            "Identified 3 new use cases for automation",
            "Customer agreed to participate in case study"
        ],
        follow_up_actions=[
            "Schedule technical deep-dive for new use cases",
            "Prepare expansion proposal for additional departments",
            "Coordinate with marketing team for case study development"
        ]
    )
    
    # 6. Enroll in advocacy program
    logger.info("🤝 Enrolling in advocacy program...")
    
    engine.enroll_in_advocacy_program(customer_id, "advocacy-manager@company.com")
    
    engine.record_advocacy_activity(
        customer_id, 
        "Agreed to participate in customer case study",
        {"case_study_type": "written", "estimated_reach": 1000}
    )
    
    # 7. Update ROI metrics to show continued improvement
    logger.info("📈 Updating ROI metrics...")
    
    engine.update_roi_metric(
        customer_id, 
        "COST-001", 
        Decimal('140000'),
        {"measurement_period": "Q2 2024", "additional_savings": "Extended automation"}
    )
    
    # 8. Generate comprehensive report
    logger.info("📋 Generating value amplification report...")
    
    report = engine.generate_value_report(customer_id)
    summary = report.generate_summary()
    
    # Display results
    print("\n" + "="*60)
    print("VALUE AMPLIFICATION REPORT SUMMARY")
    print("="*60)
    print(f"Customer ID: {customer_id}")
    print(f"Total ROI: {summary.total_roi}% ({summary.roi_impact_level})")
    print(f"Milestones: {summary.achieved_milestones}/{summary.total_milestones} achieved "
          f"({summary.milestone_achievement_rate:.1f}%)")
    print(f"Session Satisfaction: {summary.average_session_satisfaction:.1f}/10")
    print(f"Advocacy Level: {summary.advocacy_level.description}")
    print(f"Active ROI Metrics: {summary.active_roi_metrics}")
    
    print(f"\nROI by Category:")
    for category, roi in report.roi_by_category.items():
        print(f"  {category.value}: {roi}%")
    
    print(f"\nTop Performing Metrics:")
    for i, metric in enumerate(report.get_top_performing_metrics(3), 1):
        print(f"  {i}. {metric.description}: {metric.calculate_improvement_percentage()}% improvement")
    
    # 9. Check advocacy candidates
    candidates = engine.get_advocacy_candidates()
    print(f"\nAdvocacy Program Candidates: {len(candidates)} customers")
    
    # 10. Export customer data
    logger.info("💾 Exporting customer data...")
    
    exported_data = engine.export_customer_data(customer_id)
    print(f"\nData export completed: {len(exported_data)} characters")
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETED SUCCESSFULLY")
    print("="*60)
    
    return engine, report

if __name__ == "__main__":
    # Run the demonstration
    engine, report = demonstrate_value_amplification_system()
    
    # Additional analysis examples
    print("\n🔍 Additional Analysis Examples:")
    
    # Get upcoming milestones
    upcoming = engine.get_upcoming_milestones("ENTERPRISE-001", 60)
    print(f"Upcoming milestones (next 60 days): {len(upcoming)}")
    
    # Calculate value velocity
    calculation_service = ValueCalculationService()
    milestones = engine.customer_milestones["ENTERPRISE-001"]
    velocity_metrics = calculation_service.calculate_value_velocity(milestones)
    print(f"Value velocity: {velocity_metrics['velocity']} milestones/month")
    
    # Generate portfolio report (single customer for demo)
    portfolio_report = engine.generate_portfolio_report(["ENTERPRISE-001"])
    portfolio_summary = portfolio_report.get_portfolio_summary()
    print(f"Portfolio average ROI: {portfolio_summary['average_roi']:.1f}%")
