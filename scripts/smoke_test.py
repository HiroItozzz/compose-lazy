import subprocess

cases = (
    ["dcp", "--help"],
    ["dcpu", "--help"],
    ["dcpe", "--help"],
)


def _test(args):
    print(f"\n------Test case: {args[0]} command------")
    result = subprocess.run(args)
    assert result.returncode == 0


if __name__ == "__main__":
    for case in cases:
        _test(case)
