import logging
import sys
from typing import Iterable

logger = logging.getLogger(__name__)


class AttrDict(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __dir__(self):
        return self.keys()


def interactive_select(
    choice_list: Iterable[str], flag: str | None = None, multiple: bool = True
) -> list[str]:

    choice_list = sorted(choice_list)
    args = []
    prompt = (
        "\nEnter your choices (e.g., 1,3,4) or 'q' to quit: "
        if multiple
        else "\nEnter your choice or 'q' to quit: "
    )
    err_msg = (
        "☓ Invalid selection. Please use valid numbers."
        if multiple
        else "☓ Invalid selection. Please use a valid number."
    )

    # Show choices
    for idx, choice in enumerate(choice_list, start=1):
        print(f"{idx:>5}. {choice}")

    # User input
    while True:
        try:
            if (choices_str := input(prompt)) in ["Q", "q"]:
                print("\nCancelled.")
                raise SystemExit

            choices = list(
                map(
                    lambda i: int(i) - 1,
                    (i.strip() for i in choices_str.split(",") if i),
                )
            )

            if not multiple and len(choices) != 1:
                raise ValueError

            for idx in choices:
                chosen = choice_list[idx]
                if flag is None:
                    args += [chosen]
                else:
                    args += [flag, chosen]

        except (ValueError, IndexError):
            print(err_msg, file=sys.stderr)
        except KeyboardInterrupt as e:
            print("\nCancelled.")
            raise e
        else:
            print()
            break
    return args
