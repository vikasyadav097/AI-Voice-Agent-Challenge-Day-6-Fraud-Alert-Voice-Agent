import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
from livekit.plugins import silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel
import murf_tts

logger = logging.getLogger("fraud_agent")

load_dotenv(".env.local")

# Load fraud cases database
FRAUD_CASES_FILE = Path("../shared-data/fraud_cases.json")
fraud_cases = []
if FRAUD_CASES_FILE.exists():
    with open(FRAUD_CASES_FILE, "r") as f:
        fraud_cases = json.load(f)
        logger.info(f"Loaded {len(fraud_cases)} fraud cases from database")
else:
    logger.warning(f"Fraud cases file not found: {FRAUD_CASES_FILE}")

# Session state
session_state = {
    "current_case": None,
    "verification_passed": False,
    "verification_attempts": 0,
    "transaction_confirmed": None,
    "call_completed": False
}


def save_fraud_cases():
    """Save the updated fraud cases back to the database"""
    with open(FRAUD_CASES_FILE, "w") as f:
        json.dump(fraud_cases, f, indent=2)
    logger.info("Fraud cases database updated")


def find_case_by_username(username: str):
    """Find a fraud case by username (case-insensitive)"""
    username_lower = username.lower().strip()
    for case in fraud_cases:
        if case["userName"].lower() == username_lower:
            return case
    return None


class FraudAlertAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a professional fraud detection representative for SecureBank.

YOUR ROLE:
You are calling customers about suspicious transactions detected on their accounts. Your job is to:
1. Introduce yourself clearly and professionally
2. Verify the customer's identity using their security question
3. Inform them about the suspicious transaction
4. Ask if they made the transaction
5. Take appropriate action based on their response

CONVERSATION FLOW:
1. GREETING & INTRODUCTION:
   - "Hello, this is the Fraud Detection Department from SecureBank."
   - "I'm calling about some unusual activity on your account."
   - "For security purposes, may I have your full name please?"

2. LOAD CASE:
   - Once you get the name, use the load_fraud_case tool to find their case
   - If no case found, politely say you cannot find their account and end the call

3. VERIFICATION:
   - Ask their security question using the verify_customer tool
   - You get 2 attempts maximum
   - If verification fails twice, politely end the call for security reasons

4. TRANSACTION DETAILS:
   - Once verified, explain the suspicious transaction clearly:
     - Amount
     - Merchant name
     - Location
     - Time
     - Card ending in XXXX
   - Use the get_transaction_details tool to get this information

5. CONFIRMATION:
   - Ask: "Did you make this transaction?"
   - Listen for clear yes or no
   - Use the confirm_transaction tool with their answer

6. CLOSING:
   - If they confirmed (safe): "Thank you for confirming. We've marked this as a legitimate transaction. Your card remains active."
   - If they denied (fraud): "I understand. We've immediately blocked your card ending in XXXX and will issue a replacement. A dispute has been filed and you will not be charged for this transaction."
   - "Is there anything else I can help you with today?"
   - "Thank you for your time. Have a great day!"

IMPORTANT RULES:
- Be calm, professional, and reassuring
- NEVER ask for full card numbers, PINs, passwords, or CVV codes
- Only use the security question from the database for verification
- Keep responses concise and clear
- If the customer seems confused, patiently re-explain
- Always confirm actions taken at the end
- Use the tools provided - don't make up information

TONE:
- Professional but warm
- Reassuring (this is a security call, not an accusation)
- Patient and clear
- Empathetic if fraud is confirmed""",
        )
    
    @function_tool
    async def load_fraud_case(
        self, 
        context: RunContext,
        username: Annotated[str, "The customer's full name"]
    ):
        """Load the fraud case for the given customer name.
        
        Args:
            username: The customer's full name
        """
        logger.info(f"Loading fraud case for: {username}")
        
        case = find_case_by_username(username)
        
        if case:
            session_state["current_case"] = case
            logger.info(f"Found case for {username} - Card ending {case['cardEnding']}")
            return f"Case found for {username}. Security identifier: {case['securityIdentifier']}. Ready to verify customer."
        else:
            logger.warning(f"No case found for username: {username}")
            return f"I apologize, but I cannot find an account under the name {username}. Please verify the spelling or contact our customer service line."
    
    @function_tool
    async def verify_customer(
        self, 
        context: RunContext,
        answer: Annotated[str, "The customer's answer to the security question"]
    ):
        """Verify the customer's identity using their security question answer.
        
        Args:
            answer: The customer's answer to the security question
        """
        if not session_state["current_case"]:
            return "Error: No case loaded. Please provide your name first."
        
        case = session_state["current_case"]
        session_state["verification_attempts"] += 1
        
        logger.info(f"Verification attempt {session_state['verification_attempts']} for {case['userName']}")
        
        # Check answer (case-insensitive)
        correct_answer = case["securityAnswer"].lower().strip()
        provided_answer = answer.lower().strip()
        
        if provided_answer == correct_answer:
            session_state["verification_passed"] = True
            logger.info(f"Verification successful for {case['userName']}")
            return "Verification successful. Thank you for confirming your identity."
        else:
            attempts_left = 2 - session_state["verification_attempts"]
            if attempts_left > 0:
                logger.warning(f"Verification failed for {case['userName']}. {attempts_left} attempts remaining")
                return f"I'm sorry, that answer doesn't match our records. You have {attempts_left} attempt(s) remaining."
            else:
                logger.warning(f"Verification failed - maximum attempts reached for {case['userName']}")
                return "I'm sorry, but for security reasons, I cannot proceed without proper verification. Please visit your nearest branch or call our customer service line. Goodbye."
    
    @function_tool
    async def get_transaction_details(self, context: RunContext):
        """Get the suspicious transaction details to read to the customer.
        
        Returns the transaction information that should be read to the customer.
        """
        if not session_state["current_case"]:
            return "Error: No case loaded."
        
        if not session_state["verification_passed"]:
            return "Error: Customer not verified yet."
        
        case = session_state["current_case"]
        
        details = f"""We detected a suspicious transaction on your card ending in {case['cardEnding']}:
- Amount: {case['transactionAmount']}
- Merchant: {case['transactionName']}
- Category: {case['transactionCategory']}
- Location: {case['transactionLocation']}
- Time: {case['transactionTime']}
- Source: {case['transactionSource']}"""
        
        logger.info(f"Transaction details retrieved for {case['userName']}")
        return details
    
    @function_tool
    async def confirm_transaction(
        self, 
        context: RunContext,
        customer_made_transaction: Annotated[bool, "True if customer confirms they made the transaction, False if they deny it"]
    ):
        """Record whether the customer confirms or denies making the transaction.
        
        Args:
            customer_made_transaction: True if legitimate, False if fraudulent
        """
        if not session_state["current_case"]:
            return "Error: No case loaded."
        
        if not session_state["verification_passed"]:
            return "Error: Customer not verified."
        
        case = session_state["current_case"]
        session_state["transaction_confirmed"] = customer_made_transaction
        session_state["call_completed"] = True
        
        # Update the case in the database
        if customer_made_transaction:
            case["status"] = "confirmed_safe"
            case["outcome"] = f"Customer confirmed transaction as legitimate on {datetime.now().isoformat()}"
            logger.info(f"Transaction marked as SAFE for {case['userName']}")
            result = f"Transaction confirmed as safe. Card ending in {case['cardEnding']} remains active. No further action needed."
        else:
            case["status"] = "confirmed_fraud"
            case["outcome"] = f"Customer denied transaction - marked as fraud on {datetime.now().isoformat()}. Card blocked and dispute filed."
            logger.info(f"Transaction marked as FRAUD for {case['userName']}")
            result = f"Transaction marked as fraudulent. Card ending in {case['cardEnding']} has been blocked immediately. A replacement card will be mailed within 3-5 business days. A dispute has been filed and you will not be charged for this transaction."
        
        # Save to database
        save_fraud_cases()
        
        return result


def prewarm(proc: JobProcess):
    """Prewarm the VAD model"""
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the fraud alert agent"""
    
    # Reset session state for new call
    global session_state
    session_state = {
        "current_case": None,
        "verification_passed": False,
        "verification_attempts": 0,
        "transaction_confirmed": None,
        "call_completed": False
    }
    
    logger.info(f"Starting fraud alert call for room: {ctx.room.name}")
    
    # Create session with Murf TTS
    session = AgentSession(
        stt=deepgram.STT(
            model="nova-3",
            language="en-US",
        ),
        llm=google.LLM(
            model="gemini-2.5-flash",
            temperature=0.5,  # Lower temperature for more consistent, professional responses
        ),
        tts=murf_tts.TTS(
            voice="en-US-ryan",
            style="Conversational",
            tokenizer=tokenize.basic.SentenceTokenizer(
                min_sentence_len=5,
            ),
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
    )
    
    # Metrics collection
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")
        
        # Log final call outcome
        if session_state["call_completed"]:
            case = session_state["current_case"]
            if case:
                logger.info(f"Call completed - {case['userName']}: {case['status']}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session with fraud agent
    fraud_agent = FraudAlertAgent()
    
    await session.start(
        agent=fraud_agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room
    await ctx.connect()
# you can do it 

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
