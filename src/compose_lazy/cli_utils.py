import logging
import sys
from typing import Iterable, Literal, overload

logger = logging.getLogger(__name__)


@overload
def interactive_select(
        candidates, flag=..., *, multiple=..., allow_zero: Literal[True]
) -> None | list[str]: ...


@overload
def interactive_select(
        candidates, flag=..., *, multiple=..., allow_zero: Literal[False] = ...
) -> list[str]: ...


def interactive_select(
        candidates: Iterable[str],
        flag: str | None = None,
        *,
        multiple: bool = True,
        allow_zero: bool = False,
) -> list[str] | None:
    """Starts general interactive session.

    When `allow_zero` is False, returns list[str].
    Only when `allow_zero` is True, may return None (if the user inputs exactly `0`).
    Despite `multiple` being True or False, the choice `0` cannot be included in multiple choices (the session continues).

    Args:
        candidates (Iterable[str]): list, set, dict, etc... and generator-like objects.
        flag (str | None, optional): Specified when each candidate needs prefix tag in list. Defaults to None.
        multiple (bool, optional): Enables multiple select. Defaults to True.
        allow_zero (bool, optional): Enables the choice `0` make it return None. Defaults to False.

    Raises:
        SystemExit: Raised when user input `q` or `Q`.
        KeyboardInterrupt: Raised when user stopped session by Ctrl+C.

    Returns:
        list[str] | None: The list of candidate name(s) user selected, or None when `0` inputed.
    """
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

    candidates = sorted(candidates)
    # Show choices
    for idx, candidate in enumerate(candidates, start=1):
        print(f"{idx:>5}. {candidate}")

    if allow_zero:
        print("\nOr 0 to enter an alternative choice.", end="")

    # User input
    while True:
        args = []

        try:
            if (choices_str := input(prompt)) in ["Q", "q"]:
                print("\nCancelled.")
                raise SystemExit

            choices = list(
                map(
                    lambda i: int(i) - 1,
                    (i.strip() for i in choices_str.split(",") if i.strip()),
                )
            )
            if allow_zero:
                if choices == [-1]:  # When input is "0"
                    return None
                if len(choices) > 1 and -1 in choices:  # When multiple input includes "0"
                    raise ValueError
            if not multiple and len(choices) != 1:
                raise ValueError
            if any((i < 0 for i in choices)):
                raise IndexError

            for idx in choices:
                chosen = candidates[idx]
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
