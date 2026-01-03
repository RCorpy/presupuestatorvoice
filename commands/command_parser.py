# commands/command_parser.py
from .command_state import CommandState

state = CommandState()  # instancia global para mantener flujo secuencial

def parse_command(command_text, model):
    tokens = command_text.split()
    last_msg = ""

    for token in tokens:
        msg = state.handle_word(token, model)
        last_msg = msg  # guardar último mensaje

    return state.active_row, last_msg

