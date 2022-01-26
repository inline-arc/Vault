def clip_text(t, lenght = 5):
    return ".".join(t.split(".")[:lenght]) + "."