def clip_text(t, lenght = 3):
    return ".".join(t.split(".")[:lenght]) + "."