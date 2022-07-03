import sys

from fresh.run import run

while True:
    text = input("fresh > ")
    result, error = run('<shell>', text)
    if error:
        print(error.as_string())
    elif result:
        if len(result.elements) == 1:
            print(result.elements[0])
        else:
            print(result)
