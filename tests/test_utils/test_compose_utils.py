from compose_lazy import utils


def test_get_compose_file_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "docker-compose.yml").touch()
    (tmp_path / "docker-compose.prod.yaml").touch()

    result = utils.get_compose_file_paths()
    assert len(result) == 2
