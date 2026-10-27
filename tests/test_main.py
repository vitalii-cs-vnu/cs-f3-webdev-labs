import pytest

from student_portal import cli
from student_portal.storage import load_group, save_group


@pytest.fixture
def data_file(monkeypatch, tmp_path):
    """Підміняє файл даних застосунку тимчасовим."""
    path = tmp_path / "group.json"
    monkeypatch.setattr(cli, "DATA_FILE", path)
    return path


def test_main_loads_and_saves_group(group, data_file, answers, capsys):
    save_group(group, data_file)
    answers("4", "Марія", "Шевчук", "0")

    cli.main()

    out = capsys.readouterr().out
    assert "Група КН-11: студентів - 3, середній бал - 76.2" in out
    assert len(load_group(data_file)) == 4


def test_main_creates_new_group(data_file, answers):
    answers("КН-12", "0")

    cli.main()

    assert load_group(data_file).name == "КН-12"


def test_main_stops_on_broken_file(data_file):
    data_file.write_text("{", encoding="utf-8")
    with pytest.raises(SystemExit, match="Не вдалося завантажити дані"):
        cli.main()


def test_menu_downloads_group(mocker, group, answers, capsys, monkeypatch):
    monkeypatch.setenv("DEKANAT_URL", "http://test/group.json")
    remote = cli.Group("КН-12")
    fetch = mocker.patch("student_portal.cli.fetch_group", return_value=remote)
    answers("11", "т", "0")

    cli.run(group)

    fetch.assert_called_once_with("http://test/group.json")
    assert group.name == "КН-12" and len(group) == 0
    assert "Групу замінено" in capsys.readouterr().out
