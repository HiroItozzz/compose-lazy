from unittest.mock import MagicMock, patch

import pytest

from fast_dcp.main import dcpe_main, dcpu_main, main


class TestMain:
    # fmt:off
    testcases_DCP_U_SINGLE_OPTION = (
        ("dcp u", "docker compose up"),
        ("dcp up", "docker compose up"),
        ("dcp u test_container", "docker compose up test_container"),
        ("dcp up test_container", "docker compose up test_container"),
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
        ("dcp u -f test.yaml -b test_container", "docker compose -f test.yaml up --build test_container"),
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
        ("dcp e container", "docker compose exec container bash"),
        ("dcp e container uv run pytest", "docker compose exec container uv run pytest"),
        ("dcp e container -f test.yaml", "docker compose -f test.yaml exec container bash"),
        ("dcp e container uv run pytest -f test.yaml", "docker compose -f test.yaml exec container uv run pytest"),
        ("dcp e container -p testproject", "docker compose -p testproject exec container bash"),
        ("dcp e container uv run pytest -p testproject", "docker compose -p testproject exec container uv run pytest"),
        ("dcp exec container", "docker compose exec container bash"),
        ("dcp exec container uv run pytest", "docker compose exec container uv run pytest"),
        ("dcp exec container -f test.yaml", "docker compose -f test.yaml exec container bash"),
        ("dcp exec container uv run pytest -f test.yaml", "docker compose -f test.yaml exec container uv run pytest"),
        ("dcp exec container -p testproject", "docker compose -p testproject exec container bash"),
        ("dcp exec container uv run pytest -p testproject",
         "docker compose -p testproject exec container uv run pytest"),
        ("dcp e container -pf dev", "docker compose --profile dev exec container bash"),
        ("dcp e container --profile dev", "docker compose --profile dev exec container bash"),
    )
    testcases_DCP_RUN_SINGLE_OPTION = (
        ("dcp run container", "docker compose run container bash"),
        ("dcp run container uv run pytest", "docker compose run container uv run pytest"),
        ("dcp run container -f test.yaml", "docker compose -f test.yaml run container bash"),
        ("dcp run container uv run pytest -f test.yaml", "docker compose -f test.yaml run container uv run pytest"),
        ("dcp run container -p testproject", "docker compose -p testproject run container bash"),
        ("dcp run container uv run pytest -p testproject",
         "docker compose -p testproject run container uv run pytest"),
        ("dcp run container -pf dev", "docker compose --profile dev run container bash"),
        ("dcp run container --profile dev", "docker compose --profile dev run container bash"),
    )
    testcases_DCP_RESTART_SINGLE_OPTION = (
        ("dcp re container", "docker compose restart container"),
        ("dcp re container1 container2", "docker compose restart container1 container2"),
        ("dcp restart container", "docker compose restart container"),
        ("dcp restart container1 container2", "docker compose restart container1 container2"),
    )
    testcases_DCP_PS_SINGLE_OPTION = (
        ("dcp ps", "docker compose ps"),
        ("dcp ps -a", "docker compose ps --all"),
        ("dcp ps --all", "docker compose ps --all"),
        ("dcp ps -st running", "docker compose ps --status running"),
        ("dcp ps --status running", "docker compose ps --status running"),
        ("dcp ps --status created", "docker compose ps --status created"),
        ("dcp ps --status restarting", "docker compose ps --status restarting"),
        ("dcp ps --status removing", "docker compose ps --status removing"),
        ("dcp ps --status paused", "docker compose ps --status paused"),
        ("dcp ps --status exited", "docker compose ps --status exited"),
        ("dcp ps --status dead", "docker compose ps --status dead"),
        ("dcp ps --status dead container1", "docker compose ps container1 --status dead"),
        ("dcp ps container1 container2", "docker compose ps container1 container2"),
        ("dcp ps container1 container2 -a", "docker compose ps container1 container2 --all"),        
        ("dcp ps -a container1 container2", "docker compose ps container1 container2 --all"),
        ("dcp ps -a container1 container2 --status exited", "docker compose ps container1 container2 --all --status exited"),
        ("dcp ps --status running -a container1 container2", "docker compose ps container1 container2 --all --status running"),

    )
    testcases_DCP_L_SINGLE_OPTION = (
        ("dcp l", "docker compose logs"),
        ("dcp l --follow", "docker compose logs -f"),
        ("dcp l -f", "docker compose logs -f"),
        ("dcp l container", "docker compose logs container"),
        ("dcp l container1 container2", "docker compose logs container1 container2"),
        ("dcp l container1 container2 -f", "docker compose logs container1 container2 -f"),
        ("dcp l container1 container2 --follow", "docker compose logs container1 container2 -f"),
        ("dcp logs", "docker compose logs"),
        ("dcp logs --follow", "docker compose logs -f"),
        ("dcp logs -f", "docker compose logs -f"),
        ("dcp logs container", "docker compose logs container"),
        ("dcp logs container1 container2", "docker compose logs container1 container2"),
        ("dcp logs container1 container2 -f", "docker compose logs container1 container2 -f"),
        ("dcp logs container1 container2 --follow", "docker compose logs container1 container2 -f"),
    )
    testcases_DCP_S_SINGLE_OPTION = (
        ("dcp s container", "docker compose stop container"),
        ("dcp s container1 container2", "docker compose stop container1 container2"),
        ("dcp stop container", "docker compose stop container"),
        ("dcp stop container1 container2", "docker compose stop container1 container2"),
    )
    testcases_DCP_DOWN_SINGLE_OPTION = (
        ("dcp down", "docker compose down"),
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
        ("dcpu test_container", "docker compose up test_container"),
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
        ("dcpe container", "docker compose exec container bash"),
        ("dcpe container -f test.yaml", "docker compose -f test.yaml exec container bash"),
        ("dcpe container uv run pytest", "docker compose exec container uv run pytest"),
        ("dcpe container -f test.yaml", "docker compose -f test.yaml exec container bash"),
        ("dcpe container uv run pytest -f test.yaml", "docker compose -f test.yaml exec container uv run pytest"),
        ("dcpe container -p testproject", "docker compose -p testproject exec container bash"),
        ("dcpe container uv run pytest -p testproject", "docker compose -p testproject exec container uv run pytest"),
        ("dcpe container -pf dev", "docker compose --profile dev exec container bash"),
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
        "dcp ps --status container1",
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
