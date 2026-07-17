MAX_HISTORY_MESSAGES = 20  # cap to avoid exceeding the model's context window


class ConversationMemory:
    """
    Holds the running message history for a single, currently active call.
    One instance lives for the lifetime of one WebSocket connection.
    """

    def __init__(self):
        self._messages: list[dict] = []

    def add_user_message(self, text: str):
        self._messages.append({"role": "user", "content": text})
        self._trim()

    def add_ai_message(self, text: str):
        self._messages.append({"role": "assistant", "content": text})
        self._trim()

    def get_messages(self) -> list[dict]:
        return list(self._messages)

    def _trim(self):
        if len(self._messages) > MAX_HISTORY_MESSAGES:
            # Keep only the most recent messages, dropping the oldest first.
            self._messages = self._messages[-MAX_HISTORY_MESSAGES:]