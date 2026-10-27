import json

import pytest

from student_portal.exceptions import StorageError
from student_portal.storage import atomic_write, load_group, save_group


def test_save_and_load_round_trip(group, tmp_path):
    path = tmp_path / "data" / "group.json"

    save_group(group, path)

    assert load_group(path) == group


def test_saved_file_is_readable_utf8_json(group, tmp_path):
    path = tmp_path / "group.json"

    save_group(group, path)

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["students"][0]["last_name"] == "Коваль"
    assert "Коваль" in path.read_text(encoding="utf-8")  # не К...


def test_load_missing_file(tmp_path):
    with pytest.raises(StorageError, match="не знайдено"):
        load_group(tmp_path / "group.json")


@pytest.mark.parametrize(
    "content",
    [
        pytest.param("{not json", id="invalid-json"),
        pytest.param('{"name": "КН-11"}', id="no-students"),
        pytest.param(
            '{"name": "КН-11", "students": [{"id": 1, "first_name": "Олена",'
            ' "last_name": "Коваль", "grades": [{"course": "Python",'
            ' "score": 105, "graded_on": "2026-10-01"}]}]}',
            id="score-out-of-range",
        ),
        pytest.param(
            '{"name": "КН-11", "students": [{"id": 1, "first_name": "Олена",'
            ' "last_name": "Коваль", "grades": [{"course": "Python",'
            ' "score": 95, "graded_on": "01.10.2026"}]}]}',
            id="bad-date",
        ),
    ],
)
def test_load_broken_file(tmp_path, content):
    path = tmp_path / "group.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(StorageError, match="неправильний формат"):
        load_group(path)


def test_atomic_write_replaces_file(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("стара версія", encoding="utf-8")

    with atomic_write(path) as file:
        file.write("нова версія")

    assert path.read_text(encoding="utf-8") == "нова версія"


def test_atomic_write_keeps_old_file_after_error(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("стара версія", encoding="utf-8")

    with pytest.raises(RuntimeError), atomic_write(path) as file:
        file.write("половина нової")
        raise RuntimeError("збій посеред запису")

    assert path.read_text(encoding="utf-8") == "стара версія"
    assert list(tmp_path.iterdir()) == [path]  # тимчасового файлу не лишилося
