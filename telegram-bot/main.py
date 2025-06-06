"""
Aetherium Telegram Bot
The Scribe's Telegram Gateway
"""

import os
import logging
import asyncio
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/telegram_bot.log')
    ]
)

logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend-api:8000")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

class AetheriumTelegramBot:
    """Aetherium Telegram Bot Handler"""
    
    def __init__(self):
        self.backend_url = BACKEND_API_URL
        self.http_client = httpx.AsyncClient()
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_text = """
🌟 *Welcome to Aetherium* 🌟

I am the Scribe's Telegram Gateway, your connection to the AI call center platform.

*Available Commands:*
/link - Link your Telegram account to Aetherium
/status - Check your connection status
/help - Show this help message

To get started, use the /link command to connect your Telegram account to your Aetherium profile.
        """
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📚 *Aetherium Telegram Bot Help* 📚

*Commands:*
/start - Welcome message and introduction
/link - Link your Telegram account to Aetherium
/status - Check your connection status
/unlink - Unlink your Telegram account
/help - Show this help message

*Features:*
• Send messages to your Scribe via Telegram
• Receive notifications from your AI workflows
• Trigger specific Invocations via commands
• Integration with voice and SMS workflows

*Getting Started:*
1. Create an account at your Aetherium web portal
2. Use /link command here to connect your accounts
3. Configure Telegram Invocations in your workflow editor
4. Start communicating with your Scribe!

For support, contact your Aetherium administrator.
        """
        
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown'
        )
    
    async def link_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /link command"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        # Create linking data
        link_data = {
            "chat_id": chat_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
        
        try:
            # Send link request to backend
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/api/telegram/link-chat",
                    json=link_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    await update.message.reply_text(
                        "✅ *Account Linked Successfully!*\n\n"
                        "Your Telegram account has been connected to Aetherium. "
                        "You can now receive notifications and send messages to your Scribe.\n\n"
                        "Use /status to check your connection status.",
                        parse_mode='Markdown'
                    )
                elif response.status_code == 400:
                    error_detail = response.json().get("detail", "Unknown error")
                    if "already linked" in error_detail:
                        await update.message.reply_text(
                            "ℹ️ *Already Linked*\n\n"
                            "This Telegram account is already linked to an Aetherium profile.\n\n"
                            "Use /status to check your connection status.",
                            parse_mode='Markdown'
                        )
                    else:
                        await update.message.reply_text(
                            f"❌ *Linking Failed*\n\n{error_detail}",
                            parse_mode='Markdown'
                        )
                else:
                    await update.message.reply_text(
                        "❌ *Linking Failed*\n\n"
                        "Unable to link your account. Please try again later or contact support.",
                        parse_mode='Markdown'
                    )
                    
        except Exception as e:
            logger.error(f"Error linking Telegram account: {e}")
            await update.message.reply_text(
                "❌ *Connection Error*\n\n"
                "Unable to connect to Aetherium services. Please try again later.",
                parse_mode='Markdown'
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        chat_id = update.effective_chat.id
        
        try:
            # Check status with backend
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.backend_url}/api/telegram/chats",
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    chats = response.json()
                    linked_chat = None
                    
                    for chat in chats:
                        if chat["chat_id"] == chat_id:
                            linked_chat = chat
                            break
                    
                    if linked_chat:
                        status_text = f"""
✅ *Account Status: Connected*

*Telegram Account:* {update.effective_user.first_name or 'Unknown'}
*Username:* @{update.effective_user.username or 'None'}
*Chat ID:* `{chat_id}`
*Linked Since:* {linked_chat['created_at'][:10]}
*Status:* {'Active' if linked_chat['is_active'] else 'Inactive'}

Your Telegram account is successfully linked to Aetherium. You can receive notifications and send messages to your Scribe.
                        """
                    else:
                        status_text = """
❌ *Account Status: Not Linked*

Your Telegram account is not linked to any Aetherium profile.

Use /link to connect your account.
                        """
                else:
                    status_text = """
⚠️ *Status Check Failed*

Unable to verify your account status. Please try again later.
                    """
                    
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            status_text = """
❌ *Connection Error*

Unable to connect to Aetherium services. Please try again later.
            """
        
        await update.message.reply_text(
            status_text,
            parse_mode='Markdown'
        )
    
    async def unlink_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unlink command"""
        chat_id = update.effective_chat.id
        
        # Create confirmation keyboard
        keyboard = [
            [
                InlineKeyboardButton("✅ Yes, Unlink", callback_data=f"unlink_confirm_{chat_id}"),
                InlineKeyboardButton("❌ Cancel", callback_data="unlink_cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚠️ *Confirm Unlinking*\n\n"
            "Are you sure you want to unlink your Telegram account from Aetherium?\n\n"
            "You will no longer receive notifications or be able to send messages to your Scribe.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("unlink_confirm_"):
            chat_id = int(query.data.split("_")[-1])
            
            try:
                # Send unlink request to backend
                async with httpx.AsyncClient() as client:
                    response = await client.delete(
                        f"{self.backend_url}/api/telegram/chats/{chat_id}",
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        await query.edit_message_text(
                            "✅ *Account Unlinked*\n\n"
                            "Your Telegram account has been successfully unlinked from Aetherium.\n\n"
                            "Use /link if you want to reconnect in the future.",
                            parse_mode='Markdown'
                        )
                    else:
                        await query.edit_message_text(
                            "❌ *Unlinking Failed*\n\n"
                            "Unable to unlink your account. Please try again later.",
                            parse_mode='Markdown'
                        )
                        
            except Exception as e:
                logger.error(f"Error unlinking account: {e}")
                await query.edit_message_text(
                    "❌ *Connection Error*\n\n"
                    "Unable to connect to Aetherium services. Please try again later.",
                    parse_mode='Markdown'
                )
                
        elif query.data == "unlink_cancel":
            await query.edit_message_text(
                "✅ *Unlinking Cancelled*\n\n"
                "Your account remains linked to Aetherium.",
                parse_mode='Markdown'
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        chat_id = update.effective_chat.id
        message_text = update.message.text
        
        # Forward message to backend for processing
        try:
            message_data = {
                "chat_id": chat_id,
                "message": message_text,
                "user_info": {
                    "username": update.effective_user.username,
                    "first_name": update.effective_user.first_name,
                    "last_name": update.effective_user.last_name
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/api/telegram/process-message",
                    json=message_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("reply"):
                        await update.message.reply_text(result["reply"])
                elif response.status_code == 404:
                    await update.message.reply_text(
                        "❌ *Account Not Linked*\n\n"
                        "Your Telegram account is not linked to Aetherium. "
                        "Use /link to connect your account first.",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        "⚠️ Unable to process your message. Please try again later."
                    )
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(
                "❌ *Processing Error*\n\n"
                "Unable to process your message. Please try again later."
            )

async def main():
    """Main function to run the bot"""
    logger.info("🤖 Starting Aetherium Telegram Bot...")
    
    # Create bot instance
    bot = AetheriumTelegramBot()
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("link", bot.link_command))
    application.add_handler(CommandHandler("status", bot.status_command))
    application.add_handler(CommandHandler("unlink", bot.unlink_command))
    application.add_handler(CallbackQueryHandler(bot.handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Start the bot
    logger.info("✅ Telegram bot is ready")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())