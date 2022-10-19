def convert_text_to_bot_format(input_text: str) -> str:
    return input_text.replace('<', '«').replace('>', '»')
