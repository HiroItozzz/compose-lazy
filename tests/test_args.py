from unittest import TestCase
from argparse import ArgumentParser


class ArgDefinerTestBase(TestCase):
    def setUp(self):
        from fast_dcp.args import ArgBuilder

        parser = ArgumentParser()
        self.definer = ArgBuilder(parser)


class TestSetDefaults(ArgDefinerTestBase):
    def setUp(self):
        super().setUp()

        def test_func(args):
            return 1

        self.test_func = test_func

    def test_set_defaults(self):
        self.definer.set_defaults(func=self.test_func)
        args = self.definer.parser.parse_args()

        self.assertEqual(args.func(args), 1)

    def test_set_defaults_NO_ATTR(self):
        from fast_dcp.process import DockerCmdProcessor

        self.definer.set_defaults()
        args = self.definer.parser.parse_args()

        # Default to an instance of `DockerCmdProcessor`.
        self.assertIsInstance(args.func, DockerCmdProcessor)


class TestAddContainerName(ArgDefinerTestBase):
    def test_add_container_name_subcmd_SINGLE_ARG(self):
        self.definer.add_container_name_subcmd(multiple=False)
        args = self.definer.parser.parse_args(["test"])

        self.assertEqual(args.container_name, ["test"])

    def test_add_container_name_subcmd_MULTIPLE_OPTION(self):
        self.definer.add_container_name_subcmd(multiple=True)
        args = self.definer.parser.parse_args(["container1"])

        self.assertEqual(args.container_name, ["container1"])

    def test_add_container_name_subcmd_MULTIPLE_ARGS_FOR_MULTIPLE_OPTION(self):
        self.definer.add_container_name_subcmd(multiple=True)
        args = self.definer.parser.parse_args(["container1", "container2"])

        # Parses multiple args.
        self.assertEqual(args.container_name, ["container1", "container2"])

    def test_add_container_name_subcmd_MULTIPLE_ARGS_FOR_SINGLE_OPTION(self):
        self.definer.add_container_name_subcmd(multiple=False)
        args, unknown = self.definer.parser.parse_known_args(["container1", "container2"])

        # Parses only 1 arg.
        self.assertEqual(args.container_name, ["container1"])
        self.assertEqual(unknown, ["container2"])

    def test_add_container_name_subcmd_NO_ARGS_FOR_SINGLE_OPTION(self):
        self.definer.add_container_name_subcmd(multiple=False)

        # Raises an error.
        self.assertRaises(SystemExit, self.definer.parser.parse_args, [])

    def test_add_container_name_subcmd_NO_ARGS_FOR_MUTILPLE_OPTION(self):
        self.definer.add_container_name_subcmd(multiple=True)
        args, unknown = self.definer.parser.parse_known_args()

        # Does not raise an error.
        self.assertEqual(args.container_name, [])
        self.assertEqual(unknown, [])


class TestAddInnerBashCmd(ArgDefinerTestBase):
    def test_inner_bash_cmd_DEFAULT(self):
        self.definer.add_inner_bash_cmd_args()
        args = self.definer.parser.parse_args()

        # Defaults to `bash`.
        self.assertEqual(args.inner_bash_cmd, ["bash"])

    def test_inner_bash_cmd_WITH_SOME_ARGS(self):
        self.definer.add_inner_bash_cmd_args()
        args = self.definer.parser.parse_args(["uv", "run", "pytest"])

        # Parses multiple args.
        self.assertEqual(args.inner_bash_cmd, ["uv", "run", "pytest"])


class TestAddFileArgs(ArgDefinerTestBase):
    def test_file_args_ABRREV(self):
        self.definer.add_file_args()
        args = self.definer.parser.parse_args(["-f", "test_file"])

        self.assertEqual(args.file, ["test_file"])

    def test_file_args_LONG(self):
        self.definer.add_file_args()
        args = self.definer.parser.parse_args(["--file", "test_file"])

        self.assertEqual(args.file, ["test_file"])

    def test_file_args_ABRREV_WITH_MULTIPLE_ARGS(self):
        self.definer.add_file_args()
        args = self.definer.parser.parse_args(["-f", "test_file_1", "test_file_2"])

        # Parses multiple args.
        self.assertEqual(args.file, ["test_file_1", "test_file_2"])

    def test_file_args_ABRREV_WITH_NO_ARGS(self):
        self.definer.add_file_args()

        # Raises an error.
        self.assertRaises(SystemExit, self.definer.parser.parse_args, ["-f"])

    def test_file_args_LONG_WITH_MULTIPLE_ARGS(self):
        self.definer.add_file_args()
        args = self.definer.parser.parse_args(["--file", "test_file_1", "test_file_2"])

        # Parses multiple args.
        self.assertEqual(args.file, ["test_file_1", "test_file_2"])

    def test_file_args_LONG_WITH_NO_ARGS(self):
        self.definer.add_file_args()

        # Raises an error.
        self.assertRaises(SystemExit, self.definer.parser.parse_args, ["--file"])


class TestAddProjectArgs(ArgDefinerTestBase):
    def test_add_project_args_ABBREV(self):
        self.definer.add_project_args()
        args = self.definer.parser.parse_args(["-p", "fast-dcp"])

        self.assertEqual(args.project, ["fast-dcp"])

    def test_add_project_args_LONG(self):
        self.definer.add_project_args()
        args = self.definer.parser.parse_args(["--project", "fast-dcp"])

        self.assertEqual(args.project, ["fast-dcp"])

    def test_add_project_args_ABBREV_WITH_NO_ARGS(self):
        self.definer.add_project_args()

        # Raises an error.
        self.assertRaises(SystemExit, self.definer.parser.parse_args, ["-p"])

    def test_add_project_args_ABBREV_WITH_MULTIPLE_ARGS(self):
        self.definer.add_project_args()
        args, unknown = self.definer.parser.parse_known_args(["-p", "project_1", "project_2"])

        # Parses only one arg.
        self.assertEqual(args.project, ["project_1"])
        self.assertEqual(unknown, ["project_2"])

    def test_add_project_args_LONG_WITH_NO_ARGS(self):
        self.definer.add_project_args()

        # Raises an error.
        self.assertRaises(SystemExit, self.definer.parser.parse_args, ["--project"])

    def test_add_project_args_LONG_WITH_MULTIPLE_ARGS(self):
        self.definer.add_project_args()
        args, unknown = self.definer.parser.parse_known_args(
            ["--project", "project_1", "project_2"]
        )

        # Parses only one arg.
        self.assertEqual(args.project, ["project_1"])
        self.assertEqual(unknown, ["project_2"])


class TestAddBuildArgs(ArgDefinerTestBase):
    def test_add_build_args_ABBREV(self):
        self.definer.add_build_args()
        args = self.definer.parser.parse_args(["-b"])

        # Stores true
        self.assertTrue(args.build)

    def test_add_build_args_LONG(self):
        self.definer.add_build_args()
        args = self.definer.parser.parse_args(["--build"])

        # Stores true
        self.assertTrue(args.build)

    def test_add_build_args_NO_ARGS(self):
        self.definer.add_build_args()
        args = self.definer.parser.parse_args()

        self.assertFalse(args.build)


class TestAddDetachArgs(ArgDefinerTestBase):
    def test_add_detach_args_ABBREV(self):
        self.definer.add_detach_args()
        args = self.definer.parser.parse_args(["-d"])

        # Stores true
        self.assertTrue(args.detach)

    def test_add_detach_args_LONG(self):
        self.definer.add_detach_args()
        args = self.definer.parser.parse_args(["--detach"])

        # Stores true
        self.assertTrue(args.detach)

    def test_add_detach_args_NO_ARGS(self):
        self.definer.add_detach_args()
        args = self.definer.parser.parse_args()

        self.assertFalse(args.detach)


class TestAddFollowArgs(ArgDefinerTestBase):
    def test_add_follow_args_ABBREV(self):
        self.definer.add_follow_args()
        args = self.definer.parser.parse_args(["-F"])

        # Stores true
        self.assertTrue(args.follow)

    def test_add_follow_args_LONG(self):
        self.definer.add_follow_args()
        args = self.definer.parser.parse_args(["--follow"])

        # Stores true
        self.assertTrue(args.follow)

    def test_add_follow_args_NO_ARGS(self):
        self.definer.add_follow_args()
        args = self.definer.parser.parse_args()

        self.assertFalse(args.follow)
