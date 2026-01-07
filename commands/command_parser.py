# commands/command_parser.py
def parse_command(command_text, model, state):
    tokens = command_text.split()
    last_msg = ""

    for token in tokens:
        msg = state.handle_word(token, model)
        last_msg = msg

    return state.active_row, last_msg



