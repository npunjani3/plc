import badLang

while True:
    text = input('badLang > ')
    result, error = badLang.run('<stdin>', text)

    if error: print(error.asString())
    else: print(result)