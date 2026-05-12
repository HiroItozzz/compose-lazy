from argparse import ArgumentParser
from unittest import TestCase

import pytest

from fast_dcp.args import ArgBuilder


# unittest
class ArgBuilderTestBase(TestCase):
    def setUp(self):

        parser = ArgumentParser()
        self.builder = ArgBuilder(parser)


# pytest
class PytestArgBuilderBase:
    def setup_method(self):
        from fast_dcp.args import ArgBuilder

        parser = ArgumentParser()
        self.builder = ArgBuilder(parser)


class TestSetDefaults(ArgBuilderTestBase):
    def setUp(self):
        super().setUp()

        def test_func(args):
            return 1

        self.test_func = test_func

    def test_set_defaults(self):
        self.builder.set_defaults(func=self.test_func)
        args = self.builder.parser.parse_args([])

        self.assertEqual(args.func(args), 1)

    def test_set_defaults_NO_ATTR(self):
        from fast_dcp.process import DockerCmdProcessor

        self.builder.set_defaults()
        args = self.builder.parser.parse_args([])

        # Default to an instance of `DockerCmdProcessor`.
        self.assertIsInstance(args.func, DockerCmdProcessor)


class TestAddCommonComposeOptions(ArgBuilderTestBase):
    def test_add_common_compose_options_ADD_CORRECT_ARGUMENTS(self):

        self.builder.add_common_compose_options()

        actions = [a.dest for a in self.builder.parser._actions]

        assert "file" in actions
        assert "profile" in actions
        assert "project" in actions

    def test_METHOD_CHAINING(self):
        result = self.builder.add_common_compose_options()

        self.assertIs(result, self.builder)


class TestAddContainerName(ArgBuilderTestBase):
    def test_add_container_name_subcmd_SINGLE_ARG(self):
        self.builder.add_container_name_subcmd(multiple=False)
        args = self.builder.parser.parse_args(["test"])

        self.assertEqual(args.container_name, ["test"])

    def test_add_container_name_subcmd_MULTIPLE_OPTION(self):
        self.builder.add_container_name_subcmd(multiple=True)
        args = self.builder.parser.parse_args(["container1"])

        self.assertEqual(args.container_name, ["container1"])

    def test_add_container_name_subcmd_MULTIPLE_ARGS_FOR_MULTIPLE_OPTION(self):
        self.builder.add_container_name_subcmd(multiple=True)
        args = self.builder.parser.parse_args(["container1", "container2"])

        # Parses multiple args.
        self.assertEqual(args.container_name, ["container1", "container2"])

    def test_add_container_name_subcmd_MULTIPLE_ARGS_FOR_SINGLE_OPTION(self):
        self.builder.add_container_name_subcmd(multiple=False)
        args, unknown = self.builder.parser.parse_known_args(["container1", "container2"])

        # Parses only 1 arg.
        self.assertEqual(args.container_name, ["container1"])
        self.assertEqual(unknown, ["container2"])

    def test_add_container_name_subcmd_NO_ARGS_FOR_SINGLE_OPTION(self):
        self.builder.add_container_name_subcmd(multiple=False)
        args = self.builder.parser.parse_args([])
        # Raises an error.
        self.assertEqual(args.container_name, [])

    def test_add_container_name_subcmd_NO_ARGS_FOR_MUTILPLE_OPTION(self):
        self.builder.add_container_name_subcmd(multiple=True)
        args, unknown = self.builder.parser.parse_known_args([])

        # Does not raise an error.
        self.assertEqual(args.container_name, [])
        self.assertEqual(unknown, [])


class TestAddInnerBashCmd(ArgBuilderTestBase):
    def test_inner_bash_cmd_DEFAULT(self):
        self.builder.add_inner_bash_cmd_args()
        args = self.builder.parser.parse_args([])

        # Defaults to `bash`.
        self.assertEqual(args.inner_bash_cmd, ["bash"])

    def test_inner_bash_cmd_WITH_SOME_ARGS(self):
        self.builder.add_inner_bash_cmd_args()
        args = self.builder.parser.parse_args(["uv", "run", "pytest"])

        # Parses multiple args.
        self.assertEqual(args.inner_bash_cmd, ["uv", "run", "pytest"])


class TestAddFileArgs(ArgBuilderTestBase):
    def test_file_args_ABRREV(self):
        self.builder._add_file_args()
        args = self.builder.parser.parse_args(["-f", "test_file"])

        self.assertEqual(args.file, ["test_file"])

    def test_file_args_LONG(self):
        self.builder._add_file_args()
        args = self.builder.parser.parse_args(["--file", "test_file"])

        self.assertEqual(args.file, ["test_file"])

    def test_file_args_ABRREV_WITH_MULTIPLE_ARGS(self):
        self.builder._add_file_args()
        args = self.builder.parser.parse_args(["-f", "test_file_1", "test_file_2"])

        # Parses multiple args.
        self.assertEqual(args.file, ["test_file_1", "test_file_2"])

    def test_file_args_ABRREV_WITH_NO_ARGS(self):
        self.builder._add_file_args()
        args = self.builder.parser.parse_args(["-f"])

        self.assertEqual(args.file, [])

    def test_file_args_LONG_WITH_MULTIPLE_ARGS(self):
        self.builder._add_file_args()
        args = self.builder.parser.parse_args(["--file", "test_file_1", "test_file_2"])

        # Parses multiple args.
        self.assertEqual(args.file, ["test_file_1", "test_file_2"])

    def test_file_args_LONG_WITH_NO_ARGS(self):
        self.builder._add_file_args()
        args = self.builder.parser.parse_args(["--file"])

        self.assertEqual(args.file, [])


class TestAddProfileArgs(ArgBuilderTestBase):
    def test_profile_args_ABRREV(self):
        self.builder._add_profile_args()
        args = self.builder.parser.parse_args(["-pf", "profile"])

        self.assertEqual(args.profile, ["profile"])

    def test_profile_args_LONG(self):
        self.builder._add_profile_args()
        args = self.builder.parser.parse_args(["--profile", "profile"])

        self.assertEqual(args.profile, ["profile"])

    def test_profile_args_ABRREV_WITH_MULTIPLE_ARGS(self):
        self.builder._add_profile_args()
        args = self.builder.parser.parse_args(["-pf", "profile_1", "profile_2"])

        # Parses multiple args.
        self.assertEqual(args.profile, ["profile_1", "profile_2"])

    def test_profile_args_ABRREV_WITH_NO_ARGS(self):
        self.builder._add_profile_args()
        args = self.builder.parser.parse_args(["-pf"])

        self.assertEqual(args.profile, [])

    def test_profile_args_LONG_WITH_MULTIPLE_ARGS(self):
        self.builder._add_profile_args()
        args = self.builder.parser.parse_args(["--profile", "profile_1", "profile_2"])

        # Parses multiple args.
        self.assertEqual(args.profile, ["profile_1", "profile_2"])

    def test_profile_args_LONG_WITH_NO_ARGS(self):
        self.builder._add_profile_args()
        args = self.builder.parser.parse_args(["--profile"])

        self.assertEqual(args.profile, [])


class TestAddProjectArgs(ArgBuilderTestBase):
    def test_add_project_args_ABBREV(self):
        self.builder._add_project_args()
        args = self.builder.parser.parse_args(["-p", "fast-dcp"])

        self.assertEqual(args.project, "fast-dcp")

    def test_add_project_args_LONG(self):
        self.builder._add_project_args()
        args = self.builder.parser.parse_args(["--project", "fast-dcp"])

        self.assertEqual(args.project, "fast-dcp")

    def test_add_project_args_ABBREV_WITH_NO_ARGS(self):
        self.builder._add_project_args()

        # Raises an error.
        self.assertRaises(SystemExit, self.builder.parser.parse_args, ["-p"])

    def test_add_project_args_ABBREV_WITH_MULTIPLE_ARGS(self):
        self.builder._add_project_args()
        args, unknown = self.builder.parser.parse_known_args(
            ["-p", "project_1", "project_2"]
        )

        # Parses only one arg.
        self.assertEqual(args.project, "project_1")
        self.assertEqual(unknown, ["project_2"])

    def test_add_project_args_LONG_WITH_NO_ARGS(self):
        self.builder._add_project_args()

        # Raises an error.
        self.assertRaises(SystemExit, self.builder.parser.parse_args, ["--project"])

    def test_add_project_args_LONG_WITH_MULTIPLE_ARGS(self):
        self.builder._add_project_args()
        args, unknown = self.builder.parser.parse_known_args(
            ["--project", "project_1", "project_2"]
        )

        # Parses only one arg.
        self.assertEqual(args.project, "project_1")
        self.assertEqual(unknown, ["project_2"])


class TestAddBuildArgs(ArgBuilderTestBase):
    def test_add_build_args_ABBREV(self):
        self.builder.add_build_args()
        args = self.builder.parser.parse_args(["-b"])

        # Stores true
        self.assertTrue(args.build)

    def test_add_build_args_LONG(self):
        self.builder.add_build_args()
        args = self.builder.parser.parse_args(["--build"])

        # Stores true
        self.assertTrue(args.build)

    def test_add_build_args_NO_ARGS(self):
        self.builder.add_build_args()
        args = self.builder.parser.parse_args([])

        self.assertFalse(args.build)


class TestAddDetachArgs(ArgBuilderTestBase):
    def test_add_detach_args_ABBREV(self):
        self.builder.add_detach_args()
        args = self.builder.parser.parse_args(["-d"])

        # Stores true
        self.assertTrue(args.detach)

    def test_add_detach_args_LONG(self):
        self.builder.add_detach_args()
        args = self.builder.parser.parse_args(["--detach"])

        # Stores true
        self.assertTrue(args.detach)

    def test_add_detach_args_NO_ARGS(self):
        self.builder.add_detach_args()
        args = self.builder.parser.parse_args([])

        self.assertFalse(args.detach)


class TestAddFollowArgs(ArgBuilderTestBase):
    def test_add_follow_args_ABBREV(self):
        self.builder.add_follow_args()
        args = self.builder.parser.parse_args(["-f"])

        # Stores true
        self.assertTrue(args.follow)

    def test_add_follow_args_LONG(self):
        self.builder.add_follow_args()
        args = self.builder.parser.parse_args(["--follow"])

        # Stores true
        self.assertTrue(args.follow)

    def test_add_follow_args_NO_ARGS(self):
        self.builder.add_follow_args()
        args = self.builder.parser.parse_args([])

        self.assertFalse(args.follow)


class TestAddAllArgs(ArgBuilderTestBase):
    """Test cases for ArgBuilder.add_all_args()"""

    def test_add_all_args_ABBREV(self):
        self.builder.add_all_args()
        args = self.builder.parser.parse_args(["-a"])

        # Stores true
        self.assertTrue(args.all)

    def test_add_all_args_LONG(self):
        self.builder.add_all_args()
        args = self.builder.parser.parse_args(["--all"])

        # Stores true
        self.assertTrue(args.all)

    def test_add_all_args_NO_ARGS(self):
        self.builder.add_all_args()
        args = self.builder.parser.parse_args([])

        self.assertFalse(args.all)


class TestAddStatusArgs(PytestArgBuilderBase):
    STATUS_CHOICES = (
        "created",
        "restarting",
        "running",
        "removing",
        "paused",
        "exited",
        "dead",
    )

    @pytest.mark.parametrize("input_status", [*STATUS_CHOICES])
    def test_add_status_args_ABBREV(self, input_status):
        self.builder.add_status_args()
        args = self.builder.parser.parse_args(["-st", input_status])

        assert args.status == input_status

    def test_add_status_args_ABBREV_WITH_MULTIPLE_ARGS(self):
        self.builder.add_status_args()
        args, unknown = self.builder.parser.parse_known_args(
            ["-st", "created", "running"]
        )

        # Parses only one arg.
        assert args.status == "created"
        assert unknown == ["running"]

    @pytest.mark.parametrize("input_status", [*STATUS_CHOICES])
    def test_add_status_args(self, input_status):
        self.builder.add_status_args()
        args = self.builder.parser.parse_args(["--status", input_status])

        assert args.status == input_status

    def test_add_status_args_WITH_MULTIPLE_ARGS(self):
        self.builder.add_status_args()
        args, unknown = self.builder.parser.parse_known_args(
            ["--status", "created", "running"]
        )

        # Parses only one arg.
        assert args.status == "created"
        assert unknown == ["running"]

    @pytest.mark.parametrize("input_status", ["", "invalid_status"])
    def test_add_status_args_ERROR(self, input_status):
        self.builder.add_status_args()

        # Raises an error.
        with pytest.raises(SystemExit) as exc_info:
            self.builder.parser.parse_args(["--status", input_status])
        exc_info.value.code != 0


class TestAddRemoveOrphansArgs(ArgBuilderTestBase):
    """Test cases for ArgBuilder.add_remove_orphans_args()"""

    def test_add_all_args_ABBREV(self):
        self.builder.add_remove_orphans_args()
        args = self.builder.parser.parse_args(["-ro"])

        # Stores true
        self.assertTrue(args.remove_orphans)

    def test_add_remove_orphans_args_LONG(self):
        self.builder.add_remove_orphans_args()
        args = self.builder.parser.parse_args(["--remove-orphans"])

        # Stores true
        self.assertTrue(args.remove_orphans)

    def test_add_remove_orphans_args_NO_ARGS(self):
        self.builder.add_remove_orphans_args()
        args = self.builder.parser.parse_args([])

        self.assertFalse(args.remove_orphans)


class TestAddWaitArgs(ArgBuilderTestBase):
    def test_add_wait_args_ABBREV(self):
        self.builder.add_wait_args()
        args = self.builder.parser.parse_args(["-w"])

        # Stores true
        self.assertTrue(args.wait)

    def test_add_wait_args_LONG(self):
        self.builder.add_wait_args()
        args = self.builder.parser.parse_args(["--wait"])

        # Stores true
        self.assertTrue(args.wait)

    def test_add_wait_args_NO_ARGS(self):
        self.builder.add_wait_args()
        args = self.builder.parser.parse_args([])

        self.assertFalse(args.wait)
