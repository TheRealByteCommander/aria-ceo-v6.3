import diskcache as dc
import json
from loguru import logger
from typing import List, Dict, Any

class MemoryManager:
    """
    Manages persistent memory (conversation history) for AutoGen agents using diskcache.
    Each agent's memory is stored under a unique key.
    """
    
    def __init__(self, cache_dir: str = "/tmp/aria_agent_memory"):
        self.cache = dc.Cache(cache_dir)
        logger.info(f"Initialized MemoryManager with cache directory: {cache_dir}")

    def get_memory(self, agent_name: str) -> List[Dict[str, Any]]:
        """
        Retrieves the conversation history for a given agent.
        
        Args:
            agent_name: The name of the agent.
            
        Returns:
            A list of messages (conversation history).
        """
        key = f"agent_memory_{agent_name}"
        try:
            # diskcache stores data as bytes, json.loads is needed
            data = self.cache.get(key)
            if data:
                return json.loads(data)
            return []
        except Exception as e:
            logger.error(f"Error retrieving memory for {agent_name}: {e}")
            return []

    def save_memory(self, agent_name: str, messages: List[Dict[str, Any]]):
        """
        Saves the current conversation history for a given agent.
        
        Args:
            agent_name: The name of the agent.
            messages: The list of messages to save.
        """
        key = f"agent_memory_{agent_name}"
        try:
            # diskcache stores data as bytes, json.dumps is needed
            self.cache.set(key, json.dumps(messages))
            logger.debug(f"Saved {len(messages)} messages for {agent_name}")
        except Exception as e:
            logger.error(f"Error saving memory for {agent_name}: {e}")
            
    def clear_memory(self, agent_name: str):
        """
        Clears the conversation history for a given agent.
        
        Args:
            agent_name: The name of the agent.
        """
        key = f"agent_memory_{agent_name}"
        try:
            del self.cache[key]
            logger.info(f"Cleared memory for {agent_name}")
        except KeyError:
            logger.warning(f"Memory for {agent_name} not found, nothing to clear.")
        except Exception as e:
            logger.error(f"Error clearing memory for {agent_name}: {e}")

    def clear_all_memory(self):
        """
        Clears all memory in the cache.
        """
        try:
            self.cache.clear()
            logger.info("Cleared all agent memory.")
        except Exception as e:
            logger.error(f"Error clearing all memory: {e}")

# Example usage (for testing)
if __name__ == "__main__":
    manager = MemoryManager()
    
    # 1. Clear all memory for a fresh start
    manager.clear_all_memory()
    
    # 2. Test saving and retrieving
    agent_name = "TestAgent"
    initial_messages = [
        {"role": "user", "content": "Hello, I am the user."},
        {"role": "assistant", "content": "Hello, I am TestAgent."}
    ]
    
    manager.save_memory(agent_name, initial_messages)
    retrieved_messages = manager.get_memory(agent_name)
    
    print(f"Retrieved messages for {agent_name}: {retrieved_messages}")
    
    # 3. Test appending (in a real scenario, AutoGen handles appending,
    # but here we simulate it by retrieving, modifying, and saving)
    new_message = {"role": "user", "content": "How are you?"}
    retrieved_messages.append(new_message)
    manager.save_memory(agent_name, retrieved_messages)
    
    final_messages = manager.get_memory(agent_name)
    print(f"Final messages for {agent_name}: {final_messages}")
    
    # 4. Test clearing
    manager.clear_memory(agent_name)
    empty_messages = manager.get_memory(agent_name)
    print(f"Messages after clearing: {empty_messages}")
