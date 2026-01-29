def callback(details):
    print("Called")

data = lambda: print("Lambda called")

try:
    data("arg")
except TypeError as e:
    print(f"Caught expected error: {e}")
