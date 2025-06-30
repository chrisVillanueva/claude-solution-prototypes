# Customer Health Scoring & Recovery Playbooks System
# Python implementation for systematic customer success management

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthTier(Enum):
    HEALTHY = "healthy"  # 80-100
    AT_RISK = "at_risk"  # 60-79
    CRITICAL = "critical"  # 40-59
    RED_ALERT = "red_alert"  # 0-39

class PlaybookType(Enum):
    POST_INCIDENT_RECOVERY = "post_incident_recovery"
    ENGAGEMENT_REVIVAL = "engagement_revival"
    VALUE_ACCELERATION = "value_acceleration"
    CHURN_PREVENTION = "churn_prevention"
    TRUST_REBUILDING = "trust_rebuilding"

class ActionStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"

@dataclass
class HealthMetrics:
    """Core health metrics for a customer"""
    engagement_score: float = 0.0  # 0-100
    value_realization_score: float = 0.0  # 0-100
    relationship_health_score: float = 0.0  # 0-100
    risk_indicators_score: float = 0.0  # 0-100 (inverse - lower is better)
    calculated_at: datetime = field(default_factory=datetime.now)
    
    def calculate_composite_score(self) -> float:
        """Calculate weighted composite health score"""
        weights = {
            'engagement': 0.35,
            'value_realization': 0.30,
            'relationship_health': 0.25,
            'risk_indicators': 0.10
        }
        
        # Risk indicators are inverted (100 - score for positive contribution)
        risk_contribution = (100 - self.risk_indicators_score) * weights['risk_indicators']
        
        composite = (
            self.engagement_score * weights['engagement'] +
            self.value_realization_score * weights['value_realization'] +
            self.relationship_health_score * weights['relationship_health'] +
            risk_contribution
        )
        
        return min(100, max(0, composite))
    
    def get_health_tier(self) -> HealthTier:
        """Determine health tier based on composite score"""
        score = self.calculate_composite_score()
        
        if score >= 80:
            return HealthTier.HEALTHY
        elif score >= 60:
            return HealthTier.AT_RISK
        elif score >= 40:
            return HealthTier.CRITICAL
        else:
            return HealthTier.RED_ALERT

@dataclass
class CustomerProfile:
    """Customer profile with context for health scoring"""
    customer_id: str
    name: str
    segment: str  # enterprise, business, startup
    contract_value: float
    start_date: datetime
    renewal_date: datetime
    industry: str
    primary_contact: Dict[str, str]
    success_manager: str
    incident_impact_level: str  # high, medium, low
    
    # Current metrics
    current_health: Optional[HealthMetrics] = None
    health_history: List[HealthMetrics] = field(default_factory=list)
    
    # Flags and metadata
    is_post_incident: bool = True
    last_engagement: Optional[datetime] = None
    trust_rebuilding_required: bool = True
    executive_escalation_required: bool = False

@dataclass
class PlaybookAction:
    """Individual action within a playbook"""
    action_id: str
    title: str
    description: str
    assigned_to: str
    due_date: datetime
    priority: str  # high, medium, low
    estimated_effort_hours: int
    dependencies: List[str] = field(default_factory=list)
    status: ActionStatus = ActionStatus.PENDING
    completion_date: Optional[datetime] = None
    outcome_notes: str = ""
    success_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RecoveryPlaybook:
    """Recovery playbook with specific actions for customer success"""
    playbook_id: str
    playbook_type: PlaybookType
    customer_id: str
    triggered_by: str  # health_score_drop, incident_impact, manual
    triggered_at: datetime
    target_completion_date: datetime
    
    # Playbook content
    objectives: List[str]
    success_criteria: Dict[str, Any]
    actions: List[PlaybookAction]
    
    # Execution tracking
    status: str = "active"  # active, completed, paused, cancelled
    completion_percentage: float = 0.0
    assigned_csm: str = ""
    executive_sponsor: Optional[str] = None
    
    # Results tracking
    baseline_health_score: Optional[float] = None
    current_health_score: Optional[float] = None
    outcome_summary: str = ""

class HealthScoreCalculator:
    """Calculates health scores based on various data inputs"""
    
    def __init__(self):
        self.weight_adjustments = {
            'post_incident': {
                'relationship_health': 1.5,  # More weight on relationship after incident
                'risk_indicators': 1.3
            },
            'enterprise': {
                'value_realization': 1.2,  # Enterprise customers focus on value
                'relationship_health': 1.1
            }
        }
    
    def calculate_engagement_score(self, customer_data: Dict[str, Any]) -> float:
        """Calculate engagement score from usage and interaction data"""
        score = 0.0
        max_score = 100.0
        
        # Login frequency (30 points)
        login_frequency = customer_data.get('logins_per_week', 0)
        login_score = min(30, (login_frequency / 5) * 30)  # Target: 5 logins/week
        score += login_score
        
        # Feature adoption (25 points)
        features_used = customer_data.get('features_used', 0)
        total_features = customer_data.get('total_available_features', 10)
        adoption_rate = features_used / total_features if total_features > 0 else 0
        adoption_score = adoption_rate * 25
        score += adoption_score
        
        # Support interaction quality (20 points)
        support_satisfaction = customer_data.get('support_satisfaction', 3.0)  # 1-5 scale
        support_score = ((support_satisfaction - 1) / 4) * 20
        score += support_score
        
        # Office hours participation (15 points)
        office_hours_attendance = customer_data.get('office_hours_attendance_rate', 0)
        score += office_hours_attendance * 15
        
        # Documentation/help usage (10 points)
        help_usage = customer_data.get('help_articles_viewed', 0)
        help_score = min(10, (help_usage / 10) * 10)  # Target: 10 articles
        score += help_score
        
        return min(max_score, score)
    
    def calculate_value_realization_score(self, customer_data: Dict[str, Any]) -> float:
        """Calculate value realization score based on outcomes and ROI"""
        score = 0.0
        max_score = 100.0
        
        # Goal achievement (40 points)
        goals_achieved = customer_data.get('goals_achieved', 0)
        total_goals = customer_data.get('total_goals_set', 1)
        goal_rate = goals_achieved / total_goals if total_goals > 0 else 0
        score += goal_rate * 40
        
        # ROI metrics (30 points)
        actual_roi = customer_data.get('measured_roi', 0)
        expected_roi = customer_data.get('expected_roi', 1)
        roi_achievement = min(1.0, actual_roi / expected_roi) if expected_roi > 0 else 0
        score += roi_achievement * 30
        
        # Business outcome tracking (20 points)
        outcomes_tracked = customer_data.get('business_outcomes_achieved', 0)
        score += min(20, outcomes_tracked * 5)  # 5 points per outcome
        
        # Time to value achievement (10 points)
        days_to_first_value = customer_data.get('days_to_first_value', 365)
        target_days = customer_data.get('target_days_to_value', 30)
        time_score = max(0, 10 - ((days_to_first_value - target_days) / target_days) * 10)
        score += max(0, time_score)
        
        return min(max_score, score)
    
    def calculate_relationship_health_score(self, customer_data: Dict[str, Any]) -> float:
        """Calculate relationship health score"""
        score = 0.0
        max_score = 100.0
        
        # NPS/CSAT scores (35 points)
        nps_score = customer_data.get('nps_score', 0)  # -100 to +100
        csat_score = customer_data.get('csat_score', 3.0)  # 1-5 scale
        
        # Convert NPS to 0-100 scale
        nps_normalized = (nps_score + 100) / 2
        nps_contribution = (nps_normalized / 100) * 20
        
        # Convert CSAT to 0-100 scale
        csat_normalized = ((csat_score - 1) / 4) * 100
        csat_contribution = (csat_normalized / 100) * 15
        
        score += nps_contribution + csat_contribution
        
        # Trust indicators (25 points)
        trust_score = customer_data.get('trust_index', 5.0)  # 1-10 scale
        trust_contribution = ((trust_score - 1) / 9) * 25
        score += trust_contribution
        
        # Stakeholder engagement (25 points)
        stakeholder_engagement = customer_data.get('stakeholder_engagement_rate', 0.5)
        score += stakeholder_engagement * 25
        
        # Communication responsiveness (15 points)
        response_time_hours = customer_data.get('avg_response_time_hours', 48)
        target_response_hours = 24
        responsiveness = max(0, 1 - ((response_time_hours - target_response_hours) / target_response_hours))
        score += responsiveness * 15
        
        return min(max_score, score)
    
    def calculate_risk_indicators_score(self, customer_data: Dict[str, Any]) -> float:
        """Calculate risk indicators score (higher = more risk)"""
        score = 0.0
        max_score = 100.0
        
        # Contract concerns (25 points)
        contract_risk_level = customer_data.get('contract_risk_level', 0)  # 0-5 scale
        score += (contract_risk_level / 5) * 25
        
        # Payment issues (20 points)
        payment_delays = customer_data.get('payment_delays_count', 0)
        payment_risk = min(1.0, payment_delays / 3)  # Max risk at 3+ delays
        score += payment_risk * 20
        
        # Competitive activity (20 points)
        competitive_activity = customer_data.get('competitive_evaluation', False)
        if competitive_activity:
            score += 20
        
        # Usage decline (15 points)
        usage_trend = customer_data.get('usage_trend_30d', 0)  # % change
        if usage_trend < -0.2:  # More than 20% decline
            score += 15
        elif usage_trend < -0.1:  # 10-20% decline
            score += 10
        
        # Support escalations (10 points)
        escalations = customer_data.get('support_escalations_30d', 0)
        escalation_risk = min(1.0, escalations / 3)  # Max risk at 3+ escalations
        score += escalation_risk * 10
        
        # Team turnover (10 points)
        key_contact_turnover = customer_data.get('key_contact_changes_90d', 0)
        turnover_risk = min(1.0, key_contact_turnover / 2)  # Max risk at 2+ changes
        score += turnover_risk * 10
        
        return min(max_score, score)
    
    def calculate_health_metrics(self, customer: CustomerProfile, customer_data: Dict[str, Any]) -> HealthMetrics:
        """Calculate comprehensive health metrics for a customer"""
        
        engagement = self.calculate_engagement_score(customer_data)
        value_realization = self.calculate_value_realization_score(customer_data)
        relationship = self.calculate_relationship_health_score(customer_data)
        risk_indicators = self.calculate_risk_indicators_score(customer_data)
        
        # Apply weight adjustments based on customer context
        if customer.is_post_incident:
            adjustments = self.weight_adjustments.get('post_incident', {})
            relationship *= adjustments.get('relationship_health', 1.0)
            risk_indicators *= adjustments.get('risk_indicators', 1.0)
        
        if customer.segment == 'enterprise':
            adjustments = self.weight_adjustments.get('enterprise', {})
            value_realization *= adjustments.get('value_realization', 1.0)
            relationship *= adjustments.get('relationship_health', 1.0)
        
        # Ensure scores don't exceed 100
        engagement = min(100, engagement)
        value_realization = min(100, value_realization)
        relationship = min(100, relationship)
        risk_indicators = min(100, risk_indicators)
        
        return HealthMetrics(
            engagement_score=engagement,
            value_realization_score=value_realization,
            relationship_health_score=relationship,
            risk_indicators_score=risk_indicators,
            calculated_at=datetime.now()
        )

class PlaybookLibrary:
    """Library of recovery playbooks with pre-defined actions"""
    
    @staticmethod
    def create_post_incident_recovery_playbook(customer: CustomerProfile) -> RecoveryPlaybook:
        """Create post-incident recovery playbook"""
        actions = [
            PlaybookAction(
                action_id="pir_001",
                title="Executive Apology Call",
                description="Schedule and conduct executive-level apology call with customer leadership",
                assigned_to="executive-team@company.com",
                due_date=datetime.now() + timedelta(days=2),
                priority="high",
                estimated_effort_hours=2,
                success_metrics={"call_completed": False, "trust_score_impact": 0}
            ),
            PlaybookAction(
                action_id="pir_002",
                title="Detailed Incident Post-Mortem Sharing",
                description="Share comprehensive post-mortem with customer including prevention measures",
                assigned_to=customer.success_manager,
                due_date=datetime.now() + timedelta(days=5),
                priority="high",
                estimated_effort_hours=4,
                success_metrics={"post_mortem_shared": False, "customer_feedback_received": False}
            ),
            PlaybookAction(
                action_id="pir_003",
                title="Trust Rebuilding Sessions",
                description="Conduct weekly trust rebuilding sessions with customer stakeholders",
                assigned_to=customer.success_manager,
                due_date=datetime.now() + timedelta(weeks=4),
                priority="medium",
                estimated_effort_hours=16,
                success_metrics={"sessions_completed": 0, "trust_score_improvement": 0}
            ),
            PlaybookAction(
                action_id="pir_004",
                title="Enhanced Monitoring Setup",
                description="Implement customer-specific monitoring and alerting",
                assigned_to="engineering-team@company.com",
                due_date=datetime.now() + timedelta(days=7),
                priority="high",
                estimated_effort_hours=8,
                success_metrics={"monitoring_implemented": False, "customer_dashboard_access": False}
            ),
            PlaybookAction(
                action_id="pir_005",
                title="Value Recovery Demonstration",
                description="Demonstrate renewed value delivery through success metrics review",
                assigned_to=customer.success_manager,
                due_date=datetime.now() + timedelta(days=14),
                priority="medium",
                estimated_effort_hours=6,
                success_metrics={"value_demonstration_completed": False, "roi_improvement_shown": False}
            )
        ]
        
        return RecoveryPlaybook(
            playbook_id=f"PIR-{customer.customer_id}-{datetime.now().strftime('%Y%m%d')}",
            playbook_type=PlaybookType.POST_INCIDENT_RECOVERY,
            customer_id=customer.customer_id,
            triggered_by="incident_impact",
            triggered_at=datetime.now(),
            target_completion_date=datetime.now() + timedelta(days=30),
            objectives=[
                "Restore customer trust and confidence",
                "Demonstrate commitment to reliability",
                "Strengthen relationship through transparency",
                "Prevent customer churn",
                "Position for future expansion"
            ],
            success_criteria={
                "trust_score_target": 7.0,
                "health_score_target": 75.0,
                "renewal_probability_target": 0.85,
                "nps_improvement_target": 20
            },
            actions=actions,
            assigned_csm=customer.success_manager
        )
    
    @staticmethod
    def create_engagement_revival_playbook(customer: CustomerProfile) -> RecoveryPlaybook:
        """Create engagement revival playbook for low engagement scores"""
        actions = [
            PlaybookAction(
                action_id="er_001",
                title="Usage Pattern Analysis",
                description="Analyze customer usage patterns to identify engagement barriers",
                assigned_to=customer.success_manager,
                due_date=datetime.now() + timedelta(days=3),
                priority="high",
                estimated_effort_hours=4,
                success_metrics={"analysis_completed": False, "barriers_identified": 0}
            ),
            PlaybookAction(
                action_id="er_002",
                title="Personalized Training Program",
                description="Design and deliver personalized training based on usage gaps",
                assigned_to="training-team@company.com",
                due_date=datetime.now() + timedelta(days=10),
                priority="high",
                estimated_effort_hours=12,
                success_metrics={"training_sessions_delivered": 0, "feature_adoption_increase": 0}
            ),
            PlaybookAction(
                action_id="er_003",
                title="Champion Identification Program",
                description="Identify and develop internal champions within customer organization",
                assigned_to=customer.success_manager,
                due_date=datetime.now() + timedelta(days=14),
                priority="medium",
                estimated_effort_hours=8,
                success_metrics={"champions_identified": 0, "champion_training_completed": False}
            ),
            PlaybookAction(
                action_id="er_004",
                title="Integration Optimization",
                description="Optimize existing integrations and identify new integration opportunities",
                assigned_to="technical-team@company.com",
                due_date=datetime.now() + timedelta(days=21),
                priority="medium",
                estimated_effort_hours=16,
                success_metrics={"integrations_optimized": 0, "new_integrations_implemented": 0}
            )
        ]
        
        return RecoveryPlaybook(
            playbook_id=f"ER-{customer.customer_id}-{datetime.now().strftime('%Y%m%d')}",
            playbook_type=PlaybookType.ENGAGEMENT_REVIVAL,
            customer_id=customer.customer_id,
            triggered_by="low_engagement_score",
            triggered_at=datetime.now(),
            target_completion_date=datetime.now() + timedelta(days=28),
            objectives=[
                "Increase product engagement and adoption",
                "Improve user experience and satisfaction",
                "Develop internal champions",
                "Optimize workflow integration"
            ],
            success_criteria={
                "engagement_score_target": 80.0,
                "login_frequency_target": 5.0,
                "feature_adoption_target": 0.7
            },
            actions=actions,
            assigned_csm=customer.success_manager
        )

class CustomerSuccessEngine:
    """Main engine for customer success management and recovery"""
    
    def __init__(self):
        self.customers: Dict[str, CustomerProfile] = {}
        self.active_playbooks: Dict[str, RecoveryPlaybook] = {}
        self.health_calculator = HealthScoreCalculator()
        self.playbook_library = PlaybookLibrary()
        
        # Thresholds for automatic playbook triggering
        self.triggers = {
            HealthTier.CRITICAL: [PlaybookType.POST_INCIDENT_RECOVERY, PlaybookType.CHURN_PREVENTION],
            HealthTier.RED_ALERT: [PlaybookType.POST_INCIDENT_RECOVERY, PlaybookType.CHURN_PREVENTION],
            'low_engagement': PlaybookType.ENGAGEMENT_REVIVAL,
            'low_value_realization': PlaybookType.VALUE_ACCELERATION
        }
    
    def add_customer(self, customer: CustomerProfile) -> None:
        """Add or update customer profile"""
        self.customers[customer.customer_id] = customer
        logger.info(f"Added customer: {customer.name} ({customer.customer_id})")
    
    def update_customer_health(self, customer_id: str, customer_data: Dict[str, Any]) -> HealthMetrics:
        """Update customer health metrics and trigger playbooks if needed"""
        customer = self.customers.get(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Calculate new health metrics
        new_health = self.health_calculator.calculate_health_metrics(customer, customer_data)
        
        # Store previous health for comparison
        previous_health = customer.current_health
        customer.current_health = new_health
        customer.health_history.append(new_health)
        customer.last_engagement = datetime.now()
        
        # Check for playbook triggers
        self._check_playbook_triggers(customer, previous_health, new_health)
        
        logger.info(f"Updated health for {customer.name}: {new_health.calculate_composite_score():.1f} ({new_health.get_health_tier().value})")
        
        return new_health
    
    def _check_playbook_triggers(self, customer: CustomerProfile, 
                                previous_health: Optional[HealthMetrics], 
                                new_health: HealthMetrics) -> None:
        """Check if new health metrics trigger any playbooks"""
        
        current_tier = new_health.get_health_tier()
        
        # Post-incident recovery for customers still affected
        if customer.is_post_incident and customer.trust_rebuilding_required:
            if not self._has_active_playbook(customer.customer_id, PlaybookType.POST_INCIDENT_RECOVERY):
                self._trigger_playbook(customer, PlaybookType.POST_INCIDENT_RECOVERY)
        
        # Critical/Red Alert health scores
        if current_tier in [HealthTier.CRITICAL, HealthTier.RED_ALERT]:
            if not self._has_active_playbook(customer.customer_id, PlaybookType.CHURN_PREVENTION):
                self._trigger_playbook(customer, PlaybookType.CHURN_PREVENTION)
        
        # Low engagement specific triggers
        if new_health.engagement_score < 60:
            if not self._has_active_playbook(customer.customer_id, PlaybookType.ENGAGEMENT_REVIVAL):
                self._trigger_playbook(customer, PlaybookType.ENGAGEMENT_REVIVAL)
        
        # Low value realization triggers
        if new_health.value_realization_score < 50:
            if not self._has_active_playbook(customer.customer_id, PlaybookType.VALUE_ACCELERATION):
                self._trigger_playbook(customer, PlaybookType.VALUE_ACCELERATION)
        
        # Significant health drop triggers
        if previous_health:
            previous_score = previous_health.calculate_composite_score()
            current_score = new_health.calculate_composite_score()
            if current_score < previous_score - 15:  # 15+ point drop
                logger.warning(f"Significant health drop for {customer.name}: {previous_score:.1f} → {current_score:.1f}")
                self._escalate_to_executive(customer, "significant_health_drop")
    
    def _has_active_playbook(self, customer_id: str, playbook_type: PlaybookType) -> bool:
        """Check if customer has an active playbook of the specified type"""
        return any(
            pb.customer_id == customer_id and 
            pb.playbook_type == playbook_type and 
            pb.status == "active"
            for pb in self.active_playbooks.values()
        )
    
    def _trigger_playbook(self, customer: CustomerProfile, playbook_type: PlaybookType) -> None:
        """Trigger a specific playbook for a customer"""
        
        if playbook_type == PlaybookType.POST_INCIDENT_RECOVERY:
            playbook = self.playbook_library.create_post_incident_recovery_playbook(customer)
        elif playbook_type == PlaybookType.ENGAGEMENT_REVIVAL:
            playbook = self.playbook_library.create_engagement_revival_playbook(customer)
        else:
            logger.warning(f"Playbook type {playbook_type} not implemented yet")
            return
        
        # Set baseline health score
        if customer.current_health:
            playbook.baseline_health_score = customer.current_health.calculate_composite_score()
        
        self.active_playbooks[playbook.playbook_id] = playbook
        
        logger.info(f"Triggered {playbook_type.value} playbook for {customer.name}: {playbook.playbook_id}")
        
        # Notify assigned team
        self._notify_playbook_assignment(playbook)
    
    def _escalate_to_executive(self, customer: CustomerProfile, reason: str) -> None:
        """Escalate customer situation to executive team"""
        customer.executive_escalation_required = True
        
        logger.warning(f"Executive escalation required for {customer.name}: {reason}")
        
        # In a real system, this would send notifications to executives
        # and potentially trigger high-priority playbooks
    
    def _notify_playbook_assignment(self, playbook: RecoveryPlaybook) -> None:
        """Notify team members of playbook assignment"""
        # In a real system, this would send emails/Slack notifications
        logger.info(f"Playbook {playbook.playbook_id} assigned to {playbook.assigned_csm}")
    
    def update_playbook_action(self, playbook_id: str, action_id: str, 
                              status: ActionStatus, outcome_notes: str = "",
                              success_metrics: Optional[Dict[str, Any]] = None) -> None:
        """Update the status of a playbook action"""
        
        playbook = self.active_playbooks.get(playbook_id)
        if not playbook:
            raise ValueError(f"Playbook {playbook_id} not found")
        
        action = next((a for a in playbook.actions if a.action_id == action_id), None)
        if not action:
            raise ValueError(f"Action {action_id} not found in playbook {playbook_id}")
        
        action.status = status
        action.outcome_notes = outcome_notes
        
        if status == ActionStatus.COMPLETED:
            action.completion_date = datetime.now()
        
        if success_metrics:
            action.success_metrics.update(success_metrics)
        
        # Update playbook completion percentage
        completed_actions = sum(1 for a in playbook.actions if a.status == ActionStatus.COMPLETED)
        playbook.completion_percentage = (completed_actions / len(playbook.actions)) * 100
        
        logger.info(f"Updated action {action_id} in playbook {playbook_id}: {status.value}")
        
        # Check if playbook is complete
        if playbook.completion_percentage == 100:
            self._complete_playbook(playbook)
    
    def _complete_playbook(self, playbook: RecoveryPlaybook) -> None:
        """Mark playbook as completed and analyze results"""
        playbook.status = "completed"
        
        # Get current customer health for comparison
        customer = self.customers.get(playbook.customer_id)
        if customer and customer.current_health:
            playbook.current_health_score = customer.current_health.calculate_composite_score()
            
            # Calculate improvement
            if playbook.baseline_health_score:
                improvement = playbook.current_health_score - playbook.baseline_health_score
                playbook.outcome_summary = f"Health score improved by {improvement:.1f} points"
                
                if improvement >= 10:
                    logger.info(f"Playbook {playbook.playbook_id} achieved significant improvement: +{improvement:.1f}")
                elif improvement >= 0:
                    logger.info(f"Playbook {playbook.playbook_id} achieved modest improvement: +{improvement:.1f}")
                else:
                    logger.warning(f"Playbook {playbook.playbook_id} did not improve health score: {improvement:.1f}")
        
        logger.info(f"Completed playbook {playbook.playbook_id} for customer {playbook.customer_id}")
    
    def generate_recovery_report(self, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive recovery report"""
        
        if customer_id:
            customers = [self.customers[customer_id]] if customer_id in self.customers else []
        else:
            customers = list(self.customers.values())
        
        # Health distribution
        health_distribution = {tier.value: 0 for tier in HealthTier}
        total_customers = len(customers)
        
        # Recovery metrics
        post_incident_customers = 0
        health_improvements = []
        active_playbooks_count = 0
        
        for customer in customers:
            if customer.current_health:
                tier = customer.current_health.get_health_tier()
                health_distribution[tier.value] += 1
                
                if customer.is_post_incident:
                    post_incident_customers += 1
                    
                    # Calculate improvement from first recorded health
                    if len(customer.health_history) >= 2:
                        initial_score = customer.health_history[0].calculate_composite_score()
                        current_score = customer.current_health.calculate_composite_score()
                        improvement = current_score - initial_score
                        health_improvements.append(improvement)
        
        # Count active playbooks
        active_playbooks_count = sum(1 for pb in self.active_playbooks.values() if pb.status == "active")
        
        # Calculate averages
        avg_health_improvement = np.mean(health_improvements) if health_improvements else 0
        
        return {
            "report_generated_at": datetime.now().isoformat(),
            "total_customers": total_customers,
            "post_incident_customers": post_incident_customers,
            "health_distribution": health_distribution,
            "active_playbooks": active_playbooks_count,
            "recovery_metrics": {
                "average_health_improvement": round(avg_health_improvement, 2),
                "customers_with_improvement": len([i for i in health_improvements if i > 0]),
                "customers_with_decline": len([i for i in health_improvements if i < 0]),
                "significant_improvements": len([i for i in health_improvements if i >= 15])
            },
            "playbook_effectiveness": self._calculate_playbook_effectiveness()
        }
    
    def _calculate_playbook_effectiveness(self) -> Dict[str, Any]:
        """Calculate effectiveness metrics for different playbook types"""
        
        effectiveness = {}
        
        for playbook_type in PlaybookType:
            relevant_playbooks = [
                pb for pb in self.active_playbooks.values() 
                if pb.playbook_type == playbook_type
            ]
            
            if relevant_playbooks:
                completed = [pb for pb in relevant_playbooks if pb.status == "completed"]
                successful = [
                    pb for pb in completed 
                    if pb.current_health_score and pb.baseline_health_score and 
                    pb.current_health_score > pb.baseline_health_score
                ]
                
                effectiveness[playbook_type.value] = {
                    "total_triggered": len(relevant_playbooks),
                    "completed": len(completed),
                    "successful": len(successful),
                    "success_rate": len(successful) / len(completed) if completed else 0,
                    "avg_completion_percentage": np.mean([pb.completion_percentage for pb in relevant_playbooks])
                }
        
        return effectiveness

# Example usage and demonstration
def demonstrate_health_scoring_system():
    """Demonstrate the customer health scoring and recovery system"""
    
    # Initialize the system
    cs_engine = CustomerSuccessEngine()
    
    # Create sample customers
    enterprise_customer = CustomerProfile(
        customer_id="CUST-001",
        name="TechCorp Enterprise",
        segment="enterprise",
        contract_value=500000,
        start_date=datetime.now() - timedelta(days=365),
        renewal_date=datetime.now() + timedelta(days=90),
        industry="Technology",
        primary_contact={
            "name": "Sarah Johnson",
            "email": "sarah.johnson@techcorp.com",
            "role": "CTO"
        },
        success_manager="csm-sarah@company.com",
        incident_impact_level="high",
        is_post_incident=True,
        trust_rebuilding_required=True
    )
    
    business_customer = CustomerProfile(
        customer_id="CUST-002",
        name="MidSize Solutions",
        segment="business",
        contract_value=75000,
        start_date=datetime.now() - timedelta(days=180),
        renewal_date=datetime.now() + timedelta(days=150),
        industry="Financial Services",
        primary_contact={
            "name": "Mike Chen",
            "email": "mike.chen@midsize.com",
            "role": "Operations Director"
        },
        success_manager="csm-mike@company.com",
        incident_impact_level="medium",
        is_post_incident=True,
        trust_rebuilding_required=False
    )
    
    # Add customers to system
    cs_engine.add_customer(enterprise_customer)
    cs_engine.add_customer(business_customer)
    
    # Simulate customer data for health scoring
    enterprise_data = {
        'logins_per_week': 3,
        'features_used': 6,
        'total_available_features': 15,
        'support_satisfaction': 2.5,  # Low due to incident
        'office_hours_attendance_rate': 0.8,
        'help_articles_viewed': 12,
        'goals_achieved': 2,
        'total_goals_set': 5,
        'measured_roi': 1.2,
        'expected_roi': 2.0,
        'business_outcomes_achieved': 3,
        'days_to_first_value': 45,
        'target_days_to_value': 30,
        'nps_score': -20,  # Negative due to incident
        'csat_score': 2.8,
        'trust_index': 3.5,  # Low trust
        'stakeholder_engagement_rate': 0.6,
        'avg_response_time_hours': 36,
        'contract_risk_level': 3,
        'payment_delays_count': 0,
        'competitive_evaluation': True,
        'usage_trend_30d': -0.15,  # 15% decline
        'support_escalations_30d': 2,
        'key_contact_changes_90d': 1
    }
    
    business_data = {
        'logins_per_week': 4,
        'features_used': 8,
        'total_available_features': 12,
        'support_satisfaction': 3.5,
        'office_hours_attendance_rate': 0.4,
        'help_articles_viewed': 5,
        'goals_achieved': 3,
        'total_goals_set': 4,
        'measured_roi': 1.8,
        'expected_roi': 1.5,
        'business_outcomes_achieved': 2,
        'days_to_first_value': 25,
        'target_days_to_value': 30,
        'nps_score': 10,
        'csat_score': 3.8,
        'trust_index': 6.5,
        'stakeholder_engagement_rate': 0.7,
        'avg_response_time_hours': 18,
        'contract_risk_level': 1,
        'payment_delays_count': 0,
        'competitive_evaluation': False,
        'usage_trend_30d': 0.05,
        'support_escalations_30d': 0,
        'key_contact_changes_90d': 0
    }
    
    # Update health scores and trigger playbooks
    print("=== Initial Health Assessment ===")
    health1 = cs_engine.update_customer_health("CUST-001", enterprise_data)
    health2 = cs_engine.update_customer_health("CUST-002", business_data)
    
    print(f"Enterprise Customer Health: {health1.calculate_composite_score():.1f} ({health1.get_health_tier().value})")
    print(f"Business Customer Health: {health2.calculate_composite_score():.1f} ({health2.get_health_tier().value})")
    
    # Simulate playbook execution for enterprise customer
    print("\n=== Simulating Playbook Execution ===")
    
    # Find the triggered playbook
    enterprise_playbooks = [pb for pb in cs_engine.active_playbooks.values() 
                          if pb.customer_id == "CUST-001"]
    
    if enterprise_playbooks:
        playbook = enterprise_playbooks[0]
        print(f"Executing playbook: {playbook.playbook_id} ({playbook.playbook_type.value})")
        
        # Simulate completing some actions
        for i, action in enumerate(playbook.actions[:3]):  # Complete first 3 actions
            cs_engine.update_playbook_action(
                playbook.playbook_id,
                action.action_id,
                ActionStatus.COMPLETED,
                f"Action {i+1} completed successfully",
                {"completion_quality": "high"}
            )
        
        print(f"Playbook completion: {playbook.completion_percentage}%")
    
    # Simulate improved customer data after interventions
    print("\n=== Health Improvement After Interventions ===")
    
    improved_enterprise_data = enterprise_data.copy()
    improved_enterprise_data.update({
        'support_satisfaction': 4.0,  # Improved
        'nps_score': 20,  # Significant improvement
        'trust_index': 7.0,  # Trust rebuilding working
        'contract_risk_level': 1,  # Reduced risk
        'competitive_evaluation': False,  # No longer evaluating competitors
        'usage_trend_30d': 0.10  # Usage increasing
    })
    
    improved_health = cs_engine.update_customer_health("CUST-001", improved_enterprise_data)
    print(f"Improved Enterprise Health: {improved_health.calculate_composite_score():.1f} ({improved_health.get_health_tier().value})")
    
    # Generate recovery report
    print("\n=== Recovery Report ===")
    report = cs_engine.generate_recovery_report()
    print(json.dumps(report, indent=2, default=str))

if __name__ == "__main__":
    demonstrate_health_scoring_system()
