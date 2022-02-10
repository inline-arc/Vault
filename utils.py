
def clip_text(t, lenght = 4):
    t_sub = t.replace("...", "dotdotdot")
    t_clipped = ".".join(t_sub.split(".")[:lenght]) + "."
    t_reverted = t_clipped.replace("dotdotdot", "...")
    return t_reverted