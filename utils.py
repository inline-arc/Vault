def clip_text(t, lenght = 10):
    return ".".join(t.split(".")[:lenght]) + "."