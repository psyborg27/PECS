# PECS CHAT APPEND RULE

For each new Continue conversation or significant turn, append an event to:
.pecs/ai_chat_history.json

Preferred command:
python3 .pecs/tools/append_ai_chat_history.py "${workspaceFolder}" --source continue --message "<summary>"

If your Continue automation can emit a structured JSON payload, use:
python3 .pecs/tools/append_ai_chat_history.py "${workspaceFolder}" --payload-json '<json-object>'
