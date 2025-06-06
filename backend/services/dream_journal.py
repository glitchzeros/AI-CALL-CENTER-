"""
Dream Journal service
The Scribe's Autonomous Consciousness
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from database.connection import AsyncSessionLocal
from models.dream_journal import ScribeDreamJournal
from models.session import CommunicationSession, SessionMessage
from services.gemini_client import GeminiClient

logger = logging.getLogger("aetherium.dreams")

class DreamJournalService:
    """
    The Scribe's autonomous meta-analysis service
    Performs nightly analysis of conversation patterns
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.is_running = False
        self.analysis_task = None
        logger.info("🌙 Dream Journal service initialized")
    
    async def start_nightly_analysis(self):
        """Start the nightly analysis task"""
        if not self.is_running:
            self.is_running = True
            self.analysis_task = asyncio.create_task(self._nightly_analysis_loop())
            logger.info("🌟 Dream Journal nightly analysis started")
    
    async def stop(self):
        """Stop the nightly analysis"""
        self.is_running = False
        if self.analysis_task:
            self.analysis_task.cancel()
            try:
                await self.analysis_task
            except asyncio.CancelledError:
                pass
        logger.info("🌙 Dream Journal analysis stopped")
    
    async def _nightly_analysis_loop(self):
        """Main loop for nightly analysis"""
        while self.is_running:
            try:
                # Calculate next analysis time (3 AM UTC)
                now = datetime.utcnow()
                next_analysis = now.replace(hour=3, minute=0, second=0, microsecond=0)
                
                # If it's already past 3 AM today, schedule for tomorrow
                if now >= next_analysis:
                    next_analysis += timedelta(days=1)
                
                # Wait until analysis time
                wait_seconds = (next_analysis - now).total_seconds()
                logger.info(f"Next dream analysis scheduled for {next_analysis} UTC ({wait_seconds:.0f} seconds)")
                
                await asyncio.sleep(wait_seconds)
                
                # Perform analysis
                await self._perform_nightly_analysis()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Dream analysis loop error: {e}")
                # Wait 1 hour before retrying
                await asyncio.sleep(3600)
    
    async def _perform_nightly_analysis(self):
        """Perform the actual nightly analysis"""
        try:
            logger.info("🌟 Beginning nightly dream analysis...")
            
            # Get anonymized conversation data from the past 24 hours
            conversations = await self._get_anonymized_conversations()
            
            if not conversations:
                logger.info("No conversations to analyze")
                return
            
            # Analyze conversations with Gemini
            insights = await self.gemini_client.analyze_conversations_for_insights(conversations)
            
            # Store insights in dream journal
            await self._store_insights(insights)
            
            logger.info(f"Dream analysis complete: {len(insights)} insights generated from {len(conversations)} conversations")
            
        except Exception as e:
            logger.error(f"Nightly analysis error: {e}")
    
    async def _get_anonymized_conversations(self) -> List[str]:
        """Get anonymized conversation data from the past 24 hours"""
        try:
            async with AsyncSessionLocal() as db:
                # Get sessions from the past 24 hours
                yesterday = datetime.utcnow() - timedelta(days=1)
                
                sessions_result = await db.execute(
                    select(CommunicationSession).where(
                        CommunicationSession.started_at >= yesterday,
                        CommunicationSession.status == "completed"
                    ).limit(100)  # Limit to prevent overwhelming analysis
                )
                
                sessions = sessions_result.scalars().all()
                
                anonymized_conversations = []
                
                for session in sessions:
                    # Get messages for this session
                    messages_result = await db.execute(
                        select(SessionMessage).where(
                            SessionMessage.session_id == session.id
                        ).order_by(SessionMessage.timestamp)
                    )
                    
                    messages = messages_result.scalars().all()
                    
                    if messages:
                        # Create anonymized conversation text
                        conversation_text = self._anonymize_conversation(session, messages)
                        if conversation_text:
                            anonymized_conversations.append(conversation_text)
                
                return anonymized_conversations
                
        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return []
    
    def _anonymize_conversation(
        self,
        session: CommunicationSession,
        messages: List[SessionMessage]
    ) -> str:
        """Anonymize a conversation for analysis"""
        try:
            # Build conversation text with anonymization
            lines = [
                f"Session Type: {session.session_type}",
                f"Duration: {session.duration_seconds}s" if session.duration_seconds else "Duration: unknown",
                f"Outcome: {session.outcome}" if session.outcome else "Outcome: unknown",
                "---"
            ]
            
            for msg in messages:
                if msg.content:
                    # Basic anonymization - remove phone numbers, emails, names
                    content = self._anonymize_text(msg.content)
                    lines.append(f"{msg.speaker}: {content}")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Conversation anonymization error: {e}")
            return ""
    
    def _anonymize_text(self, text: str) -> str:
        """Anonymize sensitive information in text"""
        import re
        
        # Remove phone numbers
        text = re.sub(r'\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', '[PHONE]', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # Remove potential card numbers (sequences of 13-19 digits)
        text = re.sub(r'\b\d{13,19}\b', '[CARD]', text)
        
        # Remove potential names (capitalized words that might be names)
        # This is basic - in production you'd use a more sophisticated approach
        text = re.sub(r'\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\b', '[NAME]', text)
        
        return text
    
    async def _store_insights(self, insights: List[Dict[str, Any]]):
        """Store generated insights in the dream journal"""
        try:
            async with AsyncSessionLocal() as db:
                for insight in insights:
                    dream_entry = ScribeDreamJournal(
                        insight_category=insight.get("category", "general"),
                        insight_summary=insight.get("summary", ""),
                        related_invocations=insight.get("related_invocations", []),
                        anonymized_example_snippet=insight.get("example_snippet", ""),
                        severity_level=insight.get("severity", "low"),
                        metadata=insight
                    )
                    
                    db.add(dream_entry)
                
                await db.commit()
                logger.info(f"Stored {len(insights)} insights in dream journal")
                
        except Exception as e:
            logger.error(f"Error storing insights: {e}")
    
    async def get_recent_insights(
        self,
        days: int = 7,
        category: str = None,
        severity: str = None
    ) -> List[Dict[str, Any]]:
        """Get recent insights from the dream journal"""
        try:
            async with AsyncSessionLocal() as db:
                query = select(ScribeDreamJournal).where(
                    ScribeDreamJournal.timestamp >= datetime.utcnow() - timedelta(days=days)
                )
                
                if category:
                    query = query.where(ScribeDreamJournal.insight_category == category)
                
                if severity:
                    query = query.where(ScribeDreamJournal.severity_level == severity)
                
                query = query.order_by(ScribeDreamJournal.timestamp.desc())
                
                result = await db.execute(query)
                insights = result.scalars().all()
                
                return [
                    {
                        "id": insight.id,
                        "timestamp": insight.timestamp.isoformat(),
                        "category": insight.insight_category,
                        "summary": insight.insight_summary,
                        "related_invocations": insight.related_invocations,
                        "example_snippet": insight.anonymized_example_snippet,
                        "severity": insight.severity_level,
                        "metadata": insight.metadata
                    }
                    for insight in insights
                ]
                
        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            return []
    
    async def get_insight_categories(self) -> List[Dict[str, Any]]:
        """Get summary of insight categories"""
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(text("""
                    SELECT 
                        insight_category,
                        COUNT(*) as count,
                        MAX(timestamp) as latest
                    FROM scribe_dream_journal 
                    WHERE timestamp >= NOW() - INTERVAL '30 days'
                    GROUP BY insight_category
                    ORDER BY count DESC
                """))
                
                categories = []
                for row in result:
                    categories.append({
                        "category": row[0],
                        "count": row[1],
                        "latest": row[2].isoformat() if row[2] else None
                    })
                
                return categories
                
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []