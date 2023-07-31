from dataclasses import dataclass

my_dict = {"text": "1"}


@dataclass
class ExampleClass:
    text: str = "Hi"


example = ExampleClass(**my_dict)
print(example.text)
