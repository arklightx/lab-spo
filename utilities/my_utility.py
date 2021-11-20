def search_closing_bracket(text: str, i: int):
    cnt = 0
    idx = 0
    for idx in range(i, len(text)):
        if text[idx] == "{":
            cnt += 1
        elif text[idx] == "}":
            cnt -= 1
            if cnt <= 0:
                return idx


def get_position_before_item(text: str, item: str, start=0):
    i = start
    try:
        while text[i] != item:
            i += 1
    except Exception as e:
        raise Exception("Пропущен delimiter в строке")
    return i


def get_lang_by_file(file):
    lang = file.split(".")[1]
    if lang == "cpp":
        return "cpp"
    elif lang == "pas":
        return "pascal"
    elif lang == "py":
        return "python"
    else:
        raise Exception("Неподдерживаемое расширение файла")