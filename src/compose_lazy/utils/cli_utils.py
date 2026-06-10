import logging
import sys
from functools import wraps
from typing import Callable, Iterable, Literal, ParamSpec, overload

logger = logging.getLogger(__name__)

P = ParamSpec("P")


def call_safely(func: Callable[P, int]) -> Callable[P, int]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> int:
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\nCancelled.")
            return 130
        except SystemExit as e:
            return int(e.code or 0)
        except Exception:
            logger.debug("An unexpected error occurred.", exc_info=True)
            print("An unexpected error occurred.", file=sys.stderr)
            return 1

    return wrapper


def handle_config(func: Callable[P, int]) -> Callable[P, int]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> int:
        try:
            return func(*args, **kwargs)
        except (TypeError, KeyError, AttributeError):
            logger.debug("Workspace config has unexpected structure.", exc_info=True)
            print(
                "❌️ Workspace config is invalid or outdated.\n"
                "── Delete ~/.config/compose-lazy and re-register your workspaces.",
                file=sys.stderr,
            )
            return 1

    return wrapper


@overload
def interactive_select(
    candidates, flag=..., *, multiple=..., allow_zero: Literal[True]
) -> None | list[str]: ...
@overload
def interactive_select(
    candidates, flag=..., *, multiple=..., allow_zero: Literal[False] = False
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
        "Enter your choices (e.g., 1,3,4) or 'q' to quit: "
        if multiple
        else "Enter your choice or 'q' to quit: "
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
    print()

    if allow_zero:
        print(" ── Or enter 0 for a new entry.")
    # User input
    while True:
        args = []

        try:
            if (choices_str := input(prompt)) in ["Q", "q"]:
                print("Cancelled.")
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

            if choices == []:
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
        else:
            break
    return args
