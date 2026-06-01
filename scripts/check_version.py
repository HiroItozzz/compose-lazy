import os
from importlib.metadata import version

pkg = version("compose-lazy")
tag = os.environ.get("GITHUB_REF_NAME")

assert f"v{pkg}" == tag, f"v{pkg} != {tag}"
