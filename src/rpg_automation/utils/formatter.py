"""Output formatting utilities"""
from typing import List
from ..models.session import SessionState, SessionSummary, LogEntry


class SessionFormatter:
    """Formats session data for output"""
    
    @staticmethod
    def format_session_log(session: SessionState) -> str:
        """Format session log as readable text"""
        output = []
        output.append(f"\n{'='*60}")
        output.append(f"Session: {session.campaign_name}")
        output.append(f"Session ID: {session.session_id}")
        output.append(f"Party: {', '.join(session.party_members)}")
        output.append(f"{'='*60}\n")
        
        # Format log entries
        for i, log in enumerate(session.log_entries, 1):
            if log.narrative:
                output.append(log.narrative)
            else:
                output.append(log.description)
            
            # Add details for combat actions
            if log.details and log.action_type.value == "attack":
                details_str = []
                if "roll" in log.details:
                    details_str.append(f"Roll: {log.details['roll']}")
                if "damage" in log.details:
                    details_str.append(f"Damage: {log.details['damage']}")
                if details_str:
                    output.append(f"  ({', '.join(details_str)})")
            
            output.append("")  # Blank line between entries
        
        return "\n".join(output)
    
    @staticmethod
    def format_session_summary(summary: SessionSummary) -> str:
        """Format session summary"""
        output = []
        output.append(f"\n{'='*60}")
        output.append(f"CAMPAIGN SUMMARY: {summary.campaign_name}")
        output.append(f"{'='*60}\n")
        
        output.append(f"Duration: {summary.duration_seconds:.1f} seconds")
        output.append(f"Party: {', '.join(summary.party_members)}")
        output.append(f"Encounters Completed: {summary.encounters_completed}")
        
        output.append(f"\n--- Combat Statistics ---")
        output.append(f"Total Damage Dealt: {summary.total_damage_dealt}")
        output.append(f"Total Damage Taken: {summary.total_damage_taken}")
        output.append(f"Enemies Defeated: {summary.enemies_defeated}")
        output.append(f"Experience Gained: {summary.experience_gained}")
        
        if summary.critical_moments:
            output.append(f"\n--- Critical Moments ---")
            for moment in summary.critical_moments[:5]:  # Top 5
                output.append(f"  • {moment}")
        
        output.append(f"\n--- Final Outcome ---")
        output.append(summary.final_outcome)
        
        output.append(f"\n{'='*60}\n")
        
        return "\n".join(output)
    
    @staticmethod
    def save_session_to_file(session: SessionState, filepath: str):
        """Save session log to file"""
        with open(filepath, 'w') as f:
            f.write(SessionFormatter.format_session_log(session))
    
    @staticmethod
    def save_summary_to_file(summary: SessionSummary, filepath: str):
        """Save session summary to file"""
        with open(filepath, 'w') as f:
            f.write(SessionFormatter.format_session_summary(summary))
