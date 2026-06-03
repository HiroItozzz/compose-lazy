import io
from unittest.mock import MagicMock, patch

import pytest

from fast_dcp.main import dcpe_main, dcpu_main, main
from fast_dcp.process import DockerCmdProcessor as Processor


class TestMain:
    def teardown_method(self):
        Processor._get_compose_file_paths.cache_clear()

    # fmt:off
    testcases_DCP_U_SINGLE_OPTION = (
        ("dcp u", "docker compose up"),
        ("dcp up", "docker compose up"),
        ("dcp u test_service", "docker compose up test_service"),
        ("dcp up test_service", "docker compose up test_service"),
        ("dcp u test1 test2", "docker compose up test1 test2"),
        ("dcp up test1 test2", "docker compose up test1 test2"),
        ("dcp u -b", "docker compose up --build"),
        ("dcp up -b", "docker compose up --build"),
        ("dcp u --build", "docker compose up --build"),
        ("dcp up --build", "docker compose up --build"),
        ("dcp u -d", "docker compose up -d"),
        ("dcp up -d", "docker compose up -d"),
        ("dcp u -w", "docker compose up --wait"),
        ("dcp up -w", "docker compose up --wait"),
        ("dcp u --wait", "docker compose up --wait"),
        ("dcp up --wait", "docker compose up --wait"),
        ("dcp u --detach", "docker compose up -d"),
        ("dcp up --detach", "docker compose up -d"),
        ("dcp u -p test", "docker compose -p test up"),
        ("dcp up -p test", "docker compose -p test up"),
        ("dcp u --project test", "docker compose -p test up"),
        ("dcp up --project test", "docker compose -p test up"),
        ("dcp u -f test.yaml", "docker compose -f test.yaml up"),
        ("dcp up -f test.yaml", "docker compose -f test.yaml up"),
        ("dcp u --file test.yaml", "docker compose -f test.yaml up"),
        ("dcp up --file test.yaml", "docker compose -f test.yaml up"),
        ("dcp u -pf dev", "docker compose --profile dev up"),
        ("dcp up -pf dev", "docker compose --profile dev up"),
        ("dcp u --profile dev", "docker compose --profile dev up"),
        ("dcp up --profile dev", "docker compose --profile dev up"),
        ("dcp u -f test1.yaml test2.yaml", "docker compose -f test1.yaml -f test2.yaml up"),
        ("dcp up -f test1.yaml test2.yaml", "docker compose -f test1.yaml -f test2.yaml up"),
        ("dcp u --file test1.yaml test2.yaml", "docker compose -f test1.yaml -f test2.yaml up"),
        ("dcp up --file test1.yaml test2.yaml", "docker compose -f test1.yaml -f test2.yaml up"),
    )
    testcases_DCP_U_MULTIPLE_OPTIONS = (
        ("dcp u -f test.yaml -b", "docker compose -f test.yaml up --build"),
        ("dcp u -f test1.yaml test2.yaml -b", "docker compose -f test1.yaml -f test2.yaml up --build"),
        ("dcp u -f test.yaml -b test_service", "docker compose -f test.yaml up --build test_service"),
        ("dcp u -f test.yaml -b test1 test2", "docker compose -f test.yaml up --build test1 test2"),
        ("dcp u -b -d", "docker compose up --build -d"),
        ("dcp u -f test.yaml -b -d", "docker compose -f test.yaml up --build -d"),
    )
    testcases_DCP_U_MIXED_ALIASES = (
        ("dcp u -bd", "docker compose up --build -d"),
        ("dcp u -db", "docker compose up --build -d"),
        ("dcp u -bdf test.yaml", "docker compose -f test.yaml up --build -d"),
        ("dcp u -dbf test.yaml", "docker compose -f test.yaml up --build -d"),
        ("dcp u -bdf test1.yaml test2.yaml", "docker compose -f test1.yaml -f test2.yaml up --build -d"),
        ("dcp u -bdp testproject", "docker compose -p testproject up --build -d"),
        ("dcp u -dbp testproject", "docker compose -p testproject up --build -d"),
    )
    testcases_DCP_B_SINGLE_OPTION = (
        ("dcp b", "docker compose build"),
        ("dcp b -f test.yaml", "docker compose -f test.yaml build"),
        ("dcp b -f test1.yaml test2.yaml", "docker compose -f test1.yaml -f test2.yaml build"),
        ("dcp b -p testproject", "docker compose -p testproject build"),
        ("dcp build", "docker compose build"),
        ("dcp build -f test.yaml", "docker compose -f test.yaml build"),
        ("dcp build -f test1.yaml test2.yaml", "docker compose -f test1.yaml -f test2.yaml build"),
        ("dcp build -p testproject", "docker compose -p testproject build"),
        ("dcp b -pf dev", "docker compose --profile dev build"),
        ("dcp b --profile dev", "docker compose --profile dev build"),
    )
    testcases_DCP_RESTART_SINGLE_OPTION = (
        ("dcp re service", "docker compose restart service"),
        ("dcp re service1 service2", "docker compose restart service1 service2"),
        ("dcp re service1 -f test.yaml", "docker compose -f test.yaml restart service1"),
        ("dcp re service1 -f test1.yaml test2.yaml", "docker compose -f test1.yaml -f test2.yaml restart service1"),
        ("dcp re service1 -p testproject", "docker compose -p testproject restart service1"),
        ("dcp re service1 -pf profile", "docker compose --profile profile restart service1"),
        ("dcp restart service", "docker compose restart service"),
        ("dcp restart service1 service2", "docker compose restart service1 service2"),
    )
    testcases_DCP_PS_SINGLE_OPTION = (
        ("dcp ps", "docker compose ps"),
        ("dcp ps -a", "docker compose ps --all"),
        ("dcp ps --all", "docker compose ps --all"),
        ("dcp ps -f test.yaml", "docker compose -f test.yaml ps"),
        ("dcp ps -p testproject", "docker compose -p testproject ps"),
        ("dcp ps -pf profile", "docker compose --profile profile  ps"),
        ("dcp ps -st running", "docker compose ps --status running"),
        ("dcp ps --status running", "docker compose ps --status running"),
        ("dcp ps --status created", "docker compose ps --status created"),
        ("dcp ps --status restarting", "docker compose ps --status restarting"),
        ("dcp ps --status removing", "docker compose ps --status removing"),
        ("dcp ps --status paused", "docker compose ps --status paused"),
        ("dcp ps --status exited", "docker compose ps --status exited"),
        ("dcp ps --status dead", "docker compose ps --status dead"),
        ("dcp ps --status dead service1", "docker compose ps service1 --status dead"),
        ("dcp ps service1 service2", "docker compose ps service1 service2"),
        ("dcp ps service1 service2 -a", "docker compose ps service1 service2 --all"),        
        ("dcp ps -a service1 service2", "docker compose ps service1 service2 --all"),
        ("dcp ps -a service1 service2 --status exited", "docker compose ps service1 service2 --all --status exited"),
        ("dcp ps --status running -a service1 service2", "docker compose ps service1 service2 --all --status running"),

    )
    testcases_DCP_L_SINGLE_OPTION = (
        ("dcp l", "docker compose logs"),
        ("dcp l -f test.yaml", "docker compose -f test.yaml logs"),
        ("dcp l -p testproject", "docker compose -p testproject logs"),
        ("dcp l -pf profile", "docker compose --profile profile logs"),
        ("dcp l --follow", "docker compose logs -f"),
        ("dcp l -fo", "docker compose logs -f"),
        ("dcp l service", "docker compose logs service"),
        ("dcp l service1 service2", "docker compose logs service1 service2"),
        ("dcp l service1 service2 -fo", "docker compose logs service1 service2 -f"),
        ("dcp l service1 service2 --follow", "docker compose logs service1 service2 -f"),
        ("dcp logs", "docker compose logs"),
        ("dcp logs --follow", "docker compose logs -f"),
        ("dcp logs -fo", "docker compose logs -f"),
        ("dcp logs service", "docker compose logs service"),
        ("dcp logs service1 service2", "docker compose logs service1 service2"),
        ("dcp logs service1 service2 -fo", "docker compose logs service1 service2 -f"),
        ("dcp logs service1 service2 --follow", "docker compose logs service1 service2 -f"),
    )
    testcases_DCP_S_SINGLE_OPTION = (
        ("dcp s service", "docker compose stop service"),
        ("dcp s service1 service2", "docker compose stop service1 service2"),
        ("dcp s service -f test.yaml", "docker compose -f test.yaml stop service"),
        ("dcp s service -p testproject", "docker compose -p testproject stop service"),
        ("dcp s service -pf profile", "docker compose --profile profile stop service"),
        ("dcp stop service", "docker compose stop service"),
        ("dcp stop service1 service2", "docker compose stop service1 service2"),
    )
    testcases_DCP_DOWN_SINGLE_OPTION = (
        ("dcp down", "docker compose down"),
        ("dcp down -f test.yaml", "docker compose -f test.yaml down"),
        ("dcp down -p testproject", "docker compose -p testproject down"),
        ("dcp down -pf profile", "docker compose --profile profile  down"),
        ("dcp down -ro", "docker compose down --remove-orphans"),
        ("dcp down --remove-orphans", "docker compose down --remove-orphans"),
        ("dcp down -f test.yaml", "docker compose -f test.yaml down"),
        ("dcp down -f test1.yaml test2.yaml", "docker compose -f test1.yaml -f test2.yaml down"),
        ("dcp down -p testproject", "docker compose -p testproject down"),
        ("dcp down -pf dev", "docker compose --profile dev down"),
        ("dcp down --profile dev", "docker compose --profile dev down"),
    )
    # @fmt:on

    @pytest.mark.parametrize("input_cmd,expected_cmd", [
        *testcases_DCP_U_SINGLE_OPTION,
        *testcases_DCP_U_MULTIPLE_OPTIONS,
        *testcases_DCP_U_MIXED_ALIASES,
        *testcases_DCP_B_SINGLE_OPTION,
        *testcases_DCP_RESTART_SINGLE_OPTION,
        *testcases_DCP_PS_SINGLE_OPTION,
        *testcases_DCP_L_SINGLE_OPTION,
        *testcases_DCP_S_SINGLE_OPTION,
        *testcases_DCP_DOWN_SINGLE_OPTION,
    ])
    def test_run_dcp(self, input_cmd, expected_cmd):
        with patch("fast_dcp.process.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("sys.argv", input_cmd.split()):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                mock_run.assert_called_once_with(expected_cmd.split())
                assert exc_info.value.code == 0

    # fmt:off
    testcases_DCP_E_SINGLE_OPTION = (
        ("dcp e service", "docker compose exec service bash"),
        ("dcp e service uv run pytest", "docker compose exec service uv run pytest"),
        ("dcp e service -f test.yaml", "docker compose -f test.yaml exec service bash"),
        ("dcp e service uv run pytest -f test.yaml", "docker compose -f test.yaml exec service uv run pytest"),
        ("dcp e service -p testproject", "docker compose -p testproject exec service bash"),
        ("dcp e service uv run pytest -p testproject", "docker compose -p testproject exec service uv run pytest"),
        ("dcp exec service", "docker compose exec service bash"),
        ("dcp exec service uv run pytest", "docker compose exec service uv run pytest"),
        ("dcp exec service -f test.yaml", "docker compose -f test.yaml exec service bash"),
        ("dcp exec service uv run pytest -f test.yaml", "docker compose -f test.yaml exec service uv run pytest"),
        ("dcp exec service -p testproject", "docker compose -p testproject exec service bash"),
        ("dcp exec service uv run pytest -p testproject",
         "docker compose -p testproject exec service uv run pytest"),
        ("dcp e service -pf dev", "docker compose --profile dev exec service bash"),
        ("dcp e service --profile dev", "docker compose --profile dev exec service bash"),
    )
    testcases_DCP_RUN_SINGLE_OPTION = (
        ("dcp run service", "docker compose run service bash"),
        ("dcp run service uv run pytest", "docker compose run service uv run pytest"),
        ("dcp run service -f test.yaml", "docker compose -f test.yaml run service bash"),
        ("dcp run service uv run pytest -f test.yaml", "docker compose -f test.yaml run service uv run pytest"),
        ("dcp run service -p testproject", "docker compose -p testproject run service bash"),
        ("dcp run service uv run pytest -p testproject",
         "docker compose -p testproject run service uv run pytest"),
        ("dcp run service -pf dev", "docker compose --profile dev run service bash"),
        ("dcp run service --profile dev", "docker compose --profile dev run service bash"),
    )
    # fmt:on

    @pytest.mark.parametrize(
        "input_cmd,expected_cmd",
        [
            *testcases_DCP_E_SINGLE_OPTION,
            *testcases_DCP_RUN_SINGLE_OPTION,
        ],
    )
    def test_run_dcp_EXEC_RUN(self, input_cmd, expected_cmd, tmp_path, monkeypatch):
        """Tests which requires yaml files."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "compose.test.yml").write_text("services:\n  service:")
        with patch("fast_dcp.process.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("sys.argv", input_cmd.split()):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                mock_run.assert_called_once_with(expected_cmd.split())
                assert exc_info.value.code == 0

    # fmt:off
    testcases_DCPU_SINGLE_OPTION = (
        ("dcpu", "docker compose up"),
        ("dcpu test_service", "docker compose up test_service"),
        ("dcpu test1 test2", "docker compose up test1 test2"),
        ("dcpu -b", "docker compose up --build"),
        ("dcpu --build", "docker compose up --build"),
        ("dcpu -d", "docker compose up -d"),
        ("dcpu --detach", "docker compose up -d"),
        ("dcpu -w", "docker compose up --wait"),
        ("dcpu --wait", "docker compose up --wait"),
        ("dcpu -p test", "docker compose -p test up"),
        ("dcpu --project test", "docker compose -p test up"),
        ("dcpu -f test.yaml", "docker compose -f test.yaml up"),
        ("dcpu --file test.yaml", "docker compose -f test.yaml up"),
        ("dcpu -f test1.yaml test2.yaml", "docker compose -f test1.yaml -f test2.yaml up"),
        ("dcpu --file test1.yaml test2.yaml", "docker compose -f test1.yaml -f test2.yaml up"),
        ("dcpu -pf dev", "docker compose --profile dev up"),
        ("dcpu --profile dev", "docker compose --profile dev up"),
    )
    # @fmt:on
    @pytest.mark.parametrize(
        "input_cmd,expected_cmd",
        [
            *testcases_DCPU_SINGLE_OPTION,
        ],
    )
    def test_run_dcpu(self, input_cmd, expected_cmd, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "compose.test.yml").write_text("services:\n  service:")
        with patch("fast_dcp.process.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("sys.argv", input_cmd.split()):
                with pytest.raises(SystemExit) as exc_info:
                    dcpu_main()
                mock_run.assert_called_once_with(expected_cmd.split())
                assert exc_info.value.code == 0

    # fmt:off
    testcases_DCPE_SINGLE_OPTION = (
        ("dcpe service", "docker compose exec service bash"),
        ("dcpe service -f test.yaml", "docker compose -f test.yaml exec service bash"),
        ("dcpe service uv run pytest", "docker compose exec service uv run pytest"),
        ("dcpe service -f test.yaml", "docker compose -f test.yaml exec service bash"),
        ("dcpe service uv run pytest -f test.yaml", "docker compose -f test.yaml exec service uv run pytest"),
        ("dcpe service -p testproject", "docker compose -p testproject exec service bash"),
        ("dcpe service uv run pytest -p testproject", "docker compose -p testproject exec service uv run pytest"),
        ("dcpe service -pf dev", "docker compose --profile dev exec service bash"),
        ("dcpe service -pf dev prod", "docker compose --profile dev --profile prod exec service bash"),
    )
    # @fmt:on
    @pytest.mark.parametrize(
        "input_cmd,expected_cmd",
        [
            *testcases_DCPE_SINGLE_OPTION,
        ],
    )
    def test_run_dcpe(self, input_cmd, expected_cmd, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "compose.test.yml").write_text("services:\n  service:")
        with patch("fast_dcp.process.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("sys.argv", input_cmd.split()):
                with pytest.raises(SystemExit) as exc_info:
                    dcpe_main()
                mock_run.assert_called_once_with(expected_cmd.split())
                assert exc_info.value.code == 0

    # fmt:off
    testcases_DCP_EXEC_INTERACTION = (
        ("dcp e", "2\n","docker compose exec web bash"),
        ("dcp e uv run pytest", "2\n","docker compose exec web uv run pytest"),
        ("dcp e -f test.yaml", "2\n","docker compose -f test.yaml exec web bash"),
        ("dcp e uv run pytest -f test.yaml", "2\n","docker compose -f test.yaml exec web uv run pytest"),
        ("dcp e -p testproject", "2\n","docker compose -p testproject exec web bash"),
        ("dcp e uv run pytest -p testproject", "2\n","docker compose -p testproject exec web uv run pytest"),
        ("dcp e -pf dev", "2\n","docker compose --profile dev exec web bash"),
        ("dcp e --profile dev", "2\n","docker compose --profile dev exec web bash"),
    )

    testcases_DCP_RUN_INTERACTION = (
        ("dcp run", "2\n","docker compose run web bash"),
        ("dcp run uv run pytest", "2\n","docker compose run web uv run pytest"),
        ("dcp run -f test.yaml", "2\n","docker compose -f test.yaml run web bash"),
        ("dcp run uv run pytest -f test.yaml", "2\n","docker compose -f test.yaml run web uv run pytest"),
        ("dcp run -p testproject", "2\n","docker compose -p testproject run web bash"),
        ("dcp run uv run pytest -p testproject", "2\n","docker compose -p testproject run web uv run pytest"),
        ("dcp run -pf dev", "2\n","docker compose --profile dev run web bash"),
        ("dcp run --profile dev", "2\n","docker compose --profile dev run web bash"),
    )
    # fmt:on

    @pytest.mark.parametrize(
        "input_cmd,users_choice,expected_cmd",
        [
            *testcases_DCP_EXEC_INTERACTION,
            *testcases_DCP_RUN_INTERACTION,
        ],
    )
    def test_run_INTERACTION_EXEC_RUN(
        self, input_cmd, users_choice, expected_cmd, tmp_path, capsys, monkeypatch
    ):
        monkeypatch.setattr("sys.stdin", io.StringIO(users_choice))
        monkeypatch.chdir(tmp_path)
        # #1 is `db`, #2 is `web`.
        (tmp_path / "compose.test.yml").write_text("services:\n  web:\n  db:")

        with patch("fast_dcp.process.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("sys.argv", input_cmd.split()):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                mock_run.assert_called_once_with(expected_cmd.split())
                assert exc_info.value.code == 0

                std, _ = capsys.readouterr()
                assert "\n☑ Found 2 services!" in std

    # fmt:off
    testcases_INTERACTION_GENERAL = (
        ("dcp up -f", "2\n","docker compose -f compose.test_2.yml up"),
        ("dcp up -pf", "2\n","docker compose --profile prod up"),
        ("dcp up -s", "2\n","docker compose up frontend"),
        ("dcp up -f", "99\n2\n","docker compose -f compose.test_2.yml up"),
        ("dcp up -pf", "99\n2\n","docker compose --profile prod up"),
        ("dcp up -s", "99\n2\n","docker compose up frontend"),
        ("dcp up -f", "1,2\n","docker compose -f compose.test.yml -f compose.test_2.yml up"),
        ("dcp up -pf", "1,2\n","docker compose --profile dev --profile prod up"),
        ("dcp up -s", "1,2\n","docker compose up db frontend"),
    )
    # fmt:on

    @pytest.mark.parametrize(
        "input_cmd,users_choice,expected_cmd", [*testcases_INTERACTION_GENERAL]
    )
    def test_run_INTERACTION_MULTIPLE(
        self, input_cmd, users_choice, expected_cmd, tmp_path, capsys, monkeypatch
    ):
        monkeypatch.setattr("sys.stdin", io.StringIO(users_choice))
        monkeypatch.chdir(tmp_path)
        # #1 is `db`, #2 is `frontend` and #3 is `web` for services,
        # #1 is `compose.test.yml`, #2 is `compose.test_2.yml` for files,
        # #1 is `dev`, #2 is prod for profiles.
        yml = "services:\n  web:\n  db:\n    profiles:\n      [dev]"
        yml_2 = "services:\n  web:\n  frontend:\n    profiles:\n      [prod]"
        (tmp_path / "compose.test.yml").write_text(yml)
        (tmp_path / "compose.test_2.yml").write_text(yml_2)

        with patch("fast_dcp.process.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("sys.argv", input_cmd.split()):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                mock_run.assert_called_once_with(expected_cmd.split())
                assert exc_info.value.code == 0

                std, _ = capsys.readouterr()
                assert "\n☑ Found " in std

    @pytest.mark.parametrize(
        "input_cmd,expected_ws_subcmd",
        [
            ("dcp ws up", "up"),
            ("dcp ws u", "u"),
            ("dcp ws restart", "restart"),
            ("dcp ws re", "re"),
            ("dcp ws stop", "stop"),
            ("dcp ws s", "s"),
            ("dcp ws down", "down"),
            ("dcp workspace up", "up"),
            ("dcp workspace u", "u"),
            ("dcp workspace restart", "restart"),
            ("dcp workspace down", "down"),
        ],
    )
    def test_run_dcp_WS_EXECUTOR(self, input_cmd, expected_ws_subcmd):
        with patch("fast_dcp.main.ws_processor") as mock_executor:
            mock_executor.return_value = 0
            with patch("sys.argv", input_cmd.split()):
                with pytest.raises(SystemExit) as exc_info:
                    main()
            mock_executor.assert_called_once()
            args = mock_executor.call_args[0][0]
            assert args.ws_subcmd == expected_ws_subcmd
            assert exc_info.value.code == 0

    @pytest.mark.parametrize(
        "input_cmd,expected_ws_subcmd",
        [
            ("dcp ws register", "register"),
            ("dcp ws reg", "reg"),
            ("dcp ws delete", "delete"),
            ("dcp ws del", "del"),
            ("dcp ws list", "list"),
            ("dcp ws li", "li"),
            ("dcp workspace register", "register"),
            ("dcp workspace delete", "delete"),
            ("dcp workspace list", "list"),
        ],
    )
    def test_run_dcp_WS_REGISTRAR(self, input_cmd, expected_ws_subcmd):
        with patch("fast_dcp.main.ws_registrar") as mock_registrar:
            mock_registrar.return_value = 0
            with patch("sys.argv", input_cmd.split()):
                with pytest.raises(SystemExit) as exc_info:
                    main()
            mock_registrar.assert_called_once()
            args = mock_registrar.call_args[0][0]
            assert args.ws_subcmd == expected_ws_subcmd
            assert exc_info.value.code == 0

    @pytest.mark.parametrize(
        "input_cmd",
        [
            "dcp ps --status",
            "dcp ps --status invalid_status",
            "dcp ps --status service1",
        ],
    )
    def test_run_dcp_ERROR(self, input_cmd):
        with patch("fast_dcp.process.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("sys.argv", input_cmd.split()):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code != 0

    @pytest.mark.parametrize("input_cmd", ["dcp"])
    def test_run_dcp_SUBCMD_IS_NONE(self, input_cmd):
        with patch("fast_dcp.main.ArgumentParser.print_help") as mock_help:
            mock_help.return_value = MagicMock()
            with patch("sys.argv", input_cmd.split()):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                mock_help.assert_called_once_with()
                assert exc_info.value.code == 0

    @pytest.mark.parametrize("input_cmd", ["dcp ws"])
    def test_run_dcp_SUBCMD_WS_AND_WS_SUBCMD_IS_NONE(self, input_cmd):
        with patch("fast_dcp.main.ArgumentParser.print_help") as mock_help:
            mock_help.return_value = MagicMock()
            with patch("sys.argv", input_cmd.split()):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                mock_help.assert_called_once_with()
                assert exc_info.value.code == 0

    @pytest.mark.parametrize(
        "input_cmd,entrypoint",
        [
            ("dcp --version", main),
            ("dcpu --version", dcpu_main),
            ("dcpe --version", dcpe_main),
        ],
    )
    def test_version_shows_migration_notice(self, input_cmd, entrypoint, capsys):
        with patch("sys.argv", input_cmd.split()):
            with pytest.raises(SystemExit) as exc_info:
                entrypoint()

        std, _ = capsys.readouterr()
        assert exc_info.value.code == 0
        assert "fast-dcp 0.6.1" in std
        assert "fast-dcp has been renamed to compose-lazy" in std
        assert "pipx install compose-lazy" in std
        assert "uv tool install compose-" in std

    @pytest.mark.parametrize(
        "input_cmd,multiple",
        [
            ("dcp up", True),
            ("dcp build", True),
            ("dcp exec web", False),
            ("dcp run web", False),
            ("dcp restart", True),
            ("dcp ps", True),
            ("dcp logs", True),
            ("dcp stop", True),
        ],
    )
    def test_service_multiple_consistency(
        self, input_cmd, multiple, tmp_path, monkeypatch
    ):
        """Attribute `multiple` in add_service_name_subcmd and _create_service_option are consistent."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "compose.test.yml").write_text("services:\n  web:")

        with patch(
            "fast_dcp.process.DockerCmdProcessor._create_service_option", return_value=[]
        ) as mock_service:
            with patch("fast_dcp.process.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                with patch("sys.argv", input_cmd.split()):
                    with pytest.raises(SystemExit):
                        main()
                if multiple:
                    mock_service.assert_called_once_with()  # default to mutiple=True
                else:
                    mock_service.assert_called_once_with(multiple=False)
