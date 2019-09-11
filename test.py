

def animate(imgs):
    i = 0
    while True:
        yield imgs[i]
        i = i + 1 if i + 1 < len(imgs) else 0


l = ["1", "2", "3"]
x = animate(l)
print(next(x))
print(next(x))
print(next(x))
print(next(x))
print(next(x))
print(next(x))
