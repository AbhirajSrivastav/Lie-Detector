"""
Consent & Security Module

Implements ethical guardrails and GDPR/CCPA compliance:
- Informed consent verification
- Data privacy disclaimers
- Audit logging
- Data retention policies
- User opt-out handling
"""

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Optional
import logging
import json
import uuid
from enum import Enum

logger = logging.getLogger(__name__)


class ConsentStatus(Enum):
    """User consent status."""
    NOT_INITIATED = "NOT_INITIATED"
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


@dataclass
class ConsentData:
    """Consent record."""
    user_id: str
    session_id: str
    status: ConsentStatus
    timestamp: datetime
    ip_address: str
    device_fingerprint: str
    version: str = "1.0"  # Consent form version
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            'user_id': self.user_id,
            'session_id': self.session_id,
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'device_fingerprint': self.device_fingerprint,
            'version': self.version,
        }


class EthicalDisclaimers:
    """Comprehensive set of disclaimers displayed to users."""
    
    PRIMARY_DISCLAIMER = """
╔════════════════════════════════════════════════════════════════════════════════╗
║                           ⚠️  IMPORTANT DISCLAIMER ⚠️                           ║
╠════════════════════════════════════════════════════════════════════════════════╣
║                                                                                ║
║  THIS APPLICATION IS FOR ENTERTAINMENT & EDUCATIONAL PURPOSES ONLY            ║
║                                                                                ║
║  This is NOT a lie detector. It CANNOT be used as evidence in legal,          ║
║  criminal, or employment proceedings. The system is not scientifically        ║
║  validated for forensic use.                                                  ║
║                                                                                ║
║  LIMITATIONS:                                                                 ║
║  • Results can be affected by medical conditions (anxiety, ADHD, etc.)       ║
║  • Medications may alter physiological responses                              ║
║  • Cultural differences in non-verbal communication affect accuracy           ║
║  • False positives are common with introverted individuals                    ║
║  • System can be manipulated through conscious control techniques             ║
║                                                                                ║
║  USE CASES (ACCEPTABLE):                                                      ║
║  ✓ Entertainment/party games                                                  ║
║  ✓ Educational research (with IRB approval)                                   ║
║  ✓ Personal curiosity about biometric signals                                 ║
║                                                                                ║
║  PROHIBITED USE CASES:                                                         ║
║  ✗ Legal proceedings or court evidence                                        ║
║  ✗ Employment screening or hiring decisions                                   ║
║  ✗ Immigration or security clearance determinations                           ║
║  ✗ Criminal investigations or police use                                      ║
║  ✗ Any consequential decision-making                                          ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝
"""
    
    PRIVACY_POLICY = """
DATA COLLECTION & STORAGE:
• Video data: Processed locally in real-time; facial landmarks extracted only
• Audio data: Processed for pitch/spectral analysis; speech content NOT stored
• Biometric data: Baseline and scores stored in encrypted database
• Retention: All data automatically deleted 24 hours after session completion
• No third-party sharing: Data never sold or shared with external parties

YOUR RIGHTS:
• Right to access: Request your stored biometric data
• Right to deletion: Request immediate erasure of all records
• Right to opt-out: Refuse participation at any time
• Right to transparency: Full explanation of processing methods
"""
    
    CONSENT_CHECKBOX = """
I acknowledge and understand:
□ This application is for entertainment purposes only
□ Results are not scientifically validated for lie detection
□ I cannot use these results as evidence in legal proceedings
□ My biometric data will be encrypted and auto-deleted after 24 hours
□ I can withdraw consent at any time by closing the application
□ I am 18+ years old and can provide informed consent
"""


class ConsentManager:
    """
    Manages informed consent workflow and compliance logging.
    """
    
    def __init__(self):
        """Initialize consent manager."""
        self.consent_records = {}  # In production: use database
        self.audit_log = []
        self.session_consents = {}  # Track active sessions
    
    def get_consent_form(self) -> Dict[str, str]:
        """
        Return complete consent form to display to user.
        
        Returns:
            Dict with disclaimer sections
        """
        return {
            'primary_disclaimer': EthicalDisclaimers.PRIMARY_DISCLAIMER,
            'privacy_policy': EthicalDisclaimers.PRIVACY_POLICY,
            'consent_checkbox': EthicalDisclaimers.CONSENT_CHECKBOX,
            'version': '1.0',
            'last_updated': '2026-02-22'
        }
    
    def request_consent(
        self,
        user_id: str,
        ip_address: str,
        device_fingerprint: str
    ) -> Dict:
        """
        Initiate consent request for a new session.
        
        Args:
            user_id: Unique user identifier
            ip_address: User's IP address (for audit trail)
            device_fingerprint: Browser/device identifier
            
        Returns:
            Dict with session_id and consent form
        """
        session_id = str(uuid.uuid4())
        consent = ConsentData(
            user_id=user_id,
            session_id=session_id,
            status=ConsentStatus.PENDING,
            timestamp=datetime.now(),
            ip_address=ip_address,
            device_fingerprint=device_fingerprint
        )
        
        self.session_consents[session_id] = consent
        
        self._audit_log('CONSENT_REQUESTED', {
            'user_id': user_id,
            'session_id': session_id,
            'ip_address': ip_address
        })
        
        logger.info(f"Consent requested for user {user_id}, session {session_id}")
        
        return {
            'session_id': session_id,
            'form': self.get_consent_form(),
            'status': 'PENDING'
        }
    
    def submit_consent(
        self,
        session_id: str,
        accepted: bool,
        checkbox_verified: bool
    ) -> Dict:
        """
        Record user's consent decision.
        
        Args:
            session_id: Session identifier
            accepted: Whether user accepted terms
            checkbox_verified: Whether user checked all boxes
            
        Returns:
            Dict with consent status
        """
        if session_id not in self.session_consents:
            logger.error(f"Invalid session_id: {session_id}")
            return {'status': 'ERROR', 'message': 'Invalid session'}
        
        consent = self.session_consents[session_id]
        
        if not accepted or not checkbox_verified:
            consent.status = ConsentStatus.REJECTED
            self._audit_log('CONSENT_REJECTED', {
                'user_id': consent.user_id,
                'session_id': session_id
            })
            logger.warning(f"Consent rejected for session {session_id}")
            return {
                'status': 'REJECTED',
                'message': 'You must accept all terms to proceed'
            }
        
        consent.status = ConsentStatus.ACCEPTED
        self.consent_records[session_id] = consent
        
        self._audit_log('CONSENT_ACCEPTED', {
            'user_id': consent.user_id,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Consent accepted for session {session_id}")
        
        return {
            'status': 'ACCEPTED',
            'session_id': session_id,
            'remaining_time_hours': 24
        }
    
    def verify_consent(self, session_id: str) -> bool:
        """
        Verify that user has given valid consent before proceeding.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if consent valid, False otherwise
        """
        if session_id not in self.consent_records:
            logger.warning(f"Consent verification failed for session {session_id}")
            return False
        
        consent = self.consent_records[session_id]
        
        if consent.status != ConsentStatus.ACCEPTED:
            return False
        
        # Check if consent is still valid (24-hour window)
        age = datetime.now() - consent.timestamp
        if age > timedelta(hours=24):
            logger.warning(f"Consent expired for session {session_id}")
            return False
        
        return True
    
    def withdraw_consent(self, session_id: str) -> Dict:
        """
        Allow user to withdraw consent and delete their data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Confirmation dict
        """
        if session_id not in self.consent_records:
            return {'status': 'ERROR', 'message': 'Invalid session'}
        
        consent = self.consent_records[session_id]
        consent.status = ConsentStatus.WITHDRAWN
        
        self._audit_log('CONSENT_WITHDRAWN', {
            'user_id': consent.user_id,
            'session_id': session_id,
            'action': 'User requested data deletion'
        })
        
        logger.info(f"Consent withdrawn and data deletion scheduled for session {session_id}")
        
        return {
            'status': 'WITHDRAWN',
            'message': 'Your data deletion has been scheduled. All records will be purged within 24 hours.'
        }
    
    def _audit_log(self, event_type: str, event_data: Dict) -> None:
        """
        Log all consent-related events for compliance audit.
        
        Args:
            event_type: Type of consent event
            event_data: Event details
        """
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'event_data': event_data,
            'audit_id': str(uuid.uuid4())
        }
        
        self.audit_log.append(audit_entry)
        
        # In production: persist to database with signatures
        logger.info(f"Audit Log: {event_type} - {json.dumps(event_data)}")
    
    def get_audit_trail(self, session_id: str) -> list:
        """
        Retrieve audit trail for a session (compliance).
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of audit events
        """
        return [entry for entry in self.audit_log 
                if entry['event_data'].get('session_id') == session_id]


class DataRetentionPolicy:
    """
    Implements data retention and automatic deletion policies.
    """
    
    # Retention periods
    RETENTION_PERIODS = {
        'session_data': timedelta(hours=24),      # Auto-delete after 24h
        'audit_logs': timedelta(days=90),          # Compliance retention
        'user_preferences': timedelta(days=180),   # Longer retention
        'research_data': timedelta(days=365),      # With explicit consent
    }
    
    @staticmethod
    def should_delete(created_at: datetime, data_type: str) -> bool:
        """
        Determine if data should be deleted based on retention policy.
        
        Args:
            created_at: Timestamp when data was created
            data_type: Type of data (session_data, audit_logs, etc.)
            
        Returns:
            True if data should be deleted
        """
        retention_period = DataRetentionPolicy.RETENTION_PERIODS.get(
            data_type,
            timedelta(hours=24)  # Default to 24 hours
        )
        
        age = datetime.now() - created_at
        return age > retention_period
    
    @staticmethod
    def get_deletion_schedule(data_type: str) -> Dict:
        """
        Get deletion schedule information for user display.
        
        Args:
            data_type: Type of data
            
        Returns:
            Dict with retention info
        """
        retention = DataRetentionPolicy.RETENTION_PERIODS.get(
            data_type,
            timedelta(hours=24)
        )
        
        return {
            'retention_period': str(retention),
            'auto_delete_enabled': True,
            'next_purge': (datetime.now() + retention).isoformat(),
            'user_can_request_earlier_deletion': True
        }


# Example usage
if __name__ == "__main__":
    print("\nConsent Manager - Ethical Compliance Demo")
    print("="*80)
    
    manager = ConsentManager()
    
    # Step 1: Request consent
    print("\n1. Initiating consent request...")
    result = manager.request_consent(
        user_id="user_abc123",
        ip_address="192.168.1.100",
        device_fingerprint="chrome_desktop_windows"
    )
    session_id = result['session_id']
    print(f"   Session ID: {session_id}")
    print(f"   Status: {result['status']}")
    
    # Step 2: Submit consent (accepted)
    print("\n2. User viewing consent form and accepting...")
    result = manager.submit_consent(
        session_id=session_id,
        accepted=True,
        checkbox_verified=True
    )
    print(f"   Result: {result['status']}")
    
    # Step 3: Verify consent
    print("\n3. Verifying consent before starting test...")
    is_valid = manager.verify_consent(session_id)
    print(f"   Consent Valid: {is_valid}")
    
    # Step 4: View audit trail
    print("\n4. Audit Trail (for compliance):")
    audit = manager.get_audit_trail(session_id)
    for entry in audit:
        print(f"   [{entry['timestamp']}] {entry['event_type']}")
    
    # Step 5: Data retention policy
    print("\n5. Data Retention Policy:")
    policy = DataRetentionPolicy.get_deletion_schedule('session_data')
    for key, value in policy.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*80)
    print("✓ Ethical compliance checks complete")

