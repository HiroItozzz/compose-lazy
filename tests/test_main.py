from unittest.mock import MagicMock, patch

import pytest

from fast_dcp.main import dcpe_main, dcpu_main, main


class TestMain:
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

    @pytest.mark.parametrize("input_cmd,expected_cmd", [
        *testcases_DCP_U_SINGLE_OPTION,
        *testcases_DCP_U_MULTIPLE_OPTIONS,
        *testcases_DCP_U_MIXED_ALIASES,
        *testcases_DCP_B_SINGLE_OPTION,
        *testcases_DCP_E_SINGLE_OPTION,
        *testcases_DCP_RUN_SINGLE_OPTION,
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

    @pytest.mark.parametrize("input_cmd",[
        "dcp ps --status",
        "dcp ps --status invalid_status",
        "dcp ps --status service1",
    ])
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

    @pytest.mark.parametrize("input_cmd,expected_cmd", [
        *testcases_DCPU_SINGLE_OPTION,
    ])
    def test_run_dcpu(self, input_cmd, expected_cmd):
        with patch("fast_dcp.process.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("sys.argv", input_cmd.split()):
                with pytest.raises(SystemExit) as exc_info:
                    dcpu_main()
                mock_run.assert_called_once_with(expected_cmd.split())
                assert exc_info.value.code == 0

    @pytest.mark.parametrize("input_cmd,expected_cmd", [
        *testcases_DCPE_SINGLE_OPTION,
    ])
    def test_run_dcpe(self, input_cmd, expected_cmd):
        with patch("fast_dcp.process.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("sys.argv", input_cmd.split()):
                with pytest.raises(SystemExit) as exc_info:
                    dcpe_main()
                mock_run.assert_called_once_with(expected_cmd.split())
                assert exc_info.value.code == 0
