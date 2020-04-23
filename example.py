from returns.curry import partial

p = partial(lambda x: x, x=1)
print(p())
