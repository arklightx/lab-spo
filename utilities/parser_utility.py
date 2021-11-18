def search_closing_bracket(text: str, i: int):
    ...


def get_position_before_item(text: str, item: str):
    i = 0
    try:
        while text[i] != item:
            i += 1
    except Exception as e:
        raise Exception("Пропущен delimiter в строке")
    return i
