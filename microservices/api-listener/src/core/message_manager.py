
import logging 



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_message(payload):
    """
    Process WhatsApp message payload and extract conversation content if conditions are met.
    
    Args:
        payload (dict): The webhook payload containing message data
        
    Returns:
        str or None: The conversation message content if all validations pass, None otherwise
        
    Validations:
        1. data.key.remoteJid must be "120363403986445201@g.us"
        2. data.key.participantLid must exist (indicates it's a group message)
        3. Extract data.message.conversation if above conditions are met
    """
    
    try:
        # Extract nested data for easier access
        data = payload.get('data', {})
        key = data.get('key', {})
        message = data.get('message', {})
        
        # Validation 1: Check if remoteJid matches the target group
        remote_jid = key.get('remoteJid')
        target_group_id = "120363403986445201@g.us"
        
        if remote_jid != target_group_id:
            logging.info(f"Message not from target group. RemoteJid: {remote_jid}")
            return None
            
        # Validation 2: Check if participantLid exists (group message indicator)
        participant_lid = key.get('participantLid')
        if participant_lid is None:
            logging.info("ParticipantLid not found. Not a group message.")
            return None
            
        # Extract conversation content
        conversation = message.get('conversation')
        if conversation is None:
            logging.info("No conversation content found in message.")
            return None

        logging.info(f"Message processed successfully")
        return conversation
        
    except Exception as e:
        logging.info(f"Error processing message: {str(e)}")
        return None