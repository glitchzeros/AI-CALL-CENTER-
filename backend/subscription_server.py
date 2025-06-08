#!/usr/bin/env python3
"""
Simple subscription tiers server
Serves subscription data on port 8001 to bypass SQLAlchemy issues
"""

import asyncio
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

class SubscriptionHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/subscriptions/tiers':
            asyncio.run(self.handle_subscription_tiers())
        elif parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    async def handle_subscription_tiers(self):
        try:
            DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://demo_user:demo_password_123@database:5432/aetherium_demo')
            engine = create_async_engine(DATABASE_URL)
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            
            async with async_session() as db:
                query = text("""
                    SELECT id, name, description, price_usd, price_uzs, 
                           max_daily_ai_minutes, max_daily_sms, context_limit,
                           has_agentic_functions, has_agentic_constructor
                    FROM subscription_tiers 
                    ORDER BY price_usd
                """)
                
                result = await db.execute(query)
                rows = result.fetchall()
                
                tiers = []
                for row in rows:
                    tier = {
                        "id": row.id,
                        "name": row.name,
                        "display_name": row.name.replace('_', ' ').title(),
                        "description": row.description or "",
                        "price_usd": float(row.price_usd or 0),
                        "price_uzs": row.price_uzs,
                        "max_daily_ai_minutes": row.max_daily_ai_minutes,
                        "max_daily_sms": row.max_daily_sms,
                        "context_limit": row.context_limit,
                        "has_agentic_functions": row.has_agentic_functions,
                        "has_agentic_constructor": row.has_agentic_constructor,
                        "features": "[]"
                    }
                    tiers.append(tier)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(tiers).encode())
                
        except Exception as e:
            error_response = {"detail": f"Failed to get subscription tiers: {str(e)}"}
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8001), SubscriptionHandler)
    print("🚀 Subscription server starting on port 8001...")
    server.serve_forever()