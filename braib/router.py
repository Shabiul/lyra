def select_model(user_input):
    if len(user_input.split()) < 25:
        return "qwen:7b"
    return "qwen:14b"