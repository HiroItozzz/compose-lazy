import io
from unittest.mock import MagicMock

import pytest

from compose_lazy.utils import cli_utils


class TestInteraciveSelect:
    cases_f = (
        ("1\n", "-f", True, False, ["-f", "choice_1"]),
        ("2\n", "-f", True, False, ["-f", "choice_2"]),
        ("1,2\n", "-f", True, False, ["-f", "choice_1", "-f", "choice_2"]),
        (
            "  1 , 2  \n",
            "-f",
            True,
            False,
            ["-f", "choice_1", "-f", "choice_2"],
        ),
        ("3\n1\n", "-f", True, False, ["-f", "choice_1"]),
    )
    cases_pf = (
        ("1\n", "-pf", True, False, ["-pf", "choice_1"]),
        ("2\n", "-pf", True, False, ["-pf", "choice_2"]),
        ("1,2\n", "-pf", True, False, ["-pf", "choice_1", "-pf", "choice_2"]),
        (
            "  1 , 2  \n",
            "-pf",
            True,
            False,
            ["-pf", "choice_1", "-pf", "choice_2"],
        ),
        ("3\n1\n", "-pf", True, False, ["-pf", "choice_1"]),
    )
    cases_s = (
        ("1\n", None, True, False, ["choice_1"]),
        ("2\n", None, True, False, ["choice_2"]),
        ("1,2\n", None, True, False, ["choice_1", "choice_2"]),
        (
            "  1 , 2  \n",
            None,
            True,
            False,
            ["choice_1", "choice_2"],
        ),
        ("3\n1\n", None, True, False, ["choice_1"]),
    )
    cases_MULTIPLE_False = (
        ("1\n", None, False, False, ["choice_1"]),
        ("3\n1\n", None, False, False, ["choice_1"]),
    )

    @pytest.mark.parametrize(
        "keys,flag,multiple,allow_zero,expected",
        [*cases_f, *cases_pf, *cases_s, *cases_MULTIPLE_False],
    )
    def test_interactive_select(
        self, keys, flag, multiple, allow_zero, expected, monkeypatch
    ):
        monkeypatch.setattr("sys.stdin", io.StringIO(keys))
        choices = ["choice_1", "choice_2"]
        result = cli_utils.interactive_select(
            choices, flag, multiple=multiple, allow_zero=allow_zero
        )

        assert result == expected

    cases_MULTIPLE_False = (
        ("1\n", None, False, ["choice_1"]),
        ("3\n1\n", None, False, ["choice_1"]),
    )

    @pytest.mark.parametrize(
        "keys,flag,multiple,expected",
        [("1,2\n2\n", None, False, ["choice_2"])],
    )
    def test_MULTIPLE_False_TO_MULTIPLE_ARGS(
        self, keys, flag, multiple, expected, capsys, monkeypatch
    ):
        monkeypatch.setattr("sys.stdin", io.StringIO(keys))
        choices = ["choice_1", "choice_2"]
        result = cli_utils.interactive_select(choices, flag, multiple=multiple)

        _, err = capsys.readouterr()
        assert "☓ Invalid selection. Please use a valid number." in err
        assert result == expected

    cases_ALLOW_ZERO_True = (
        ("1\n", None, False, True, ["choice_1"]),
        ("0\n", None, False, True, None),
        ("0\n", None, True, True, None),
        ("0,1\n1\n", None, False, True, ["choice_1"]),
        ("0,1\n1\n", None, True, True, ["choice_1"]),
    )

    @pytest.mark.parametrize(
        "keys,flag,multiple,allow_zero,expected",
        [*cases_ALLOW_ZERO_True],
    )
    def test_interactive_select_ALLOW_ZERO(
        self, keys, flag, multiple, allow_zero, expected, capsys, monkeypatch
    ):
        monkeypatch.setattr("sys.stdin", io.StringIO(keys))
        choices = ["choice_1", "choice_2"]
        result = cli_utils.interactive_select(
            choices, flag, multiple=multiple, allow_zero=allow_zero
        )
        out, _ = capsys.readouterr()
        assert result == expected
        assert "Or '0'" in out

    @pytest.mark.parametrize("keys", ["3\n1\n", "abc\n1\n", "0\n-1\n1\n"])
    def test_interactive_select_VALUE_ERROR(self, keys, capsys, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO(keys))
        choices = ["choice_1", "choice_2"]
        cli_utils.interactive_select(choices, "--test")

        _, err = capsys.readouterr()
        assert "☓ Invalid selection. Please use valid numbers." in err

    def test_interactive_select_KEYBOARD_INTERRUPT(self, capsys, monkeypatch):
        monkeypatch.setattr("builtins.input", MagicMock(side_effect=KeyboardInterrupt))
        choices = ["test_1", "test_2"]

        with pytest.raises(KeyboardInterrupt):
            cli_utils.interactive_select(choices, "--test")

        captured = capsys.readouterr()

        assert "\nCancelled." in captured.out

    @pytest.mark.parametrize(
        "values",
        ["q\n", "Q\n"],
    )
    def test_sinteractive_select_QUIT(self, values, capsys, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO(values))
        choices = ["test_1", "test_2"]

        with pytest.raises(SystemExit):
            cli_utils.interactive_select(choices, "--test")

        captured = capsys.readouterr()

        assert "\nCancelled." in captured.out
