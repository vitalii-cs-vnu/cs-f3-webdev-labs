from collections.abc import Callable
from pathlib import Path

import pytest

from student_portal.exceptions import JournalFormatError, StorageError
from student_portal.journal import import_journal, parse_entries, read_rows

HEADER = "student_id;course;score;graded_on"

type JournalWriter = Callable[..., Path]


@pytest.fixture
def write_journal(tmp_path: Path) -> JournalWriter:
    """Фабрика файлів журналу: рядки даних додаються після заголовка."""

    def write(*rows: str, header: str = HEADER, encoding: str = "utf-8") -> Path:
        path = tmp_path / "journal.csv"
        path.write_text("\n".join([header, *rows]) + "\n", encoding=encoding)
        return path

    return write


def test_import_adds_all_grades(group, write_journal):
    path = write_journal(
        "1;Вебтехнології;91;2026-10-20", "3;Вебтехнології;74;2026-10-20"
    )

    count = import_journal(group, path)

    assert count == 2
    assert [g.score for g in group.get(3).grades_for("Вебтехнології")] == [74]


def test_import_strips_course_name(group, write_journal):
    import_journal(group, write_journal("3; Вебтехнології ;74;2026-10-20"))
    assert group.get(3).grades[0].course == "Вебтехнології"


def test_excel_bom_is_accepted(group, write_journal):
    path = write_journal("3;Вебтехнології;74;2026-10-20", encoding="utf-8-sig")
    assert import_journal(group, path) == 1


@pytest.mark.parametrize(
    ("row", "message"),
    [
        pytest.param("2;Вебтехнології;105;2026-10-20", "від 0 до 100", id="score"),
        pytest.param("2;Вебтехнології;abc;2026-10-20", "invalid literal", id="text"),
        pytest.param("2;Вебтехнології;91;20.10.2026", "isoformat", id="date"),
        pytest.param("2;Вебтехнології;91", "", id="missing-column"),
        pytest.param("x;Вебтехнології;91;2026-10-20", "invalid literal", id="id"),
        pytest.param("42;Вебтехнології;91;2026-10-20", "id=42", id="unknown-id"),
    ],
)
def test_bad_row_is_reported_with_line_number(group, write_journal, row, message):
    path = write_journal("1;Вебтехнології;91;2026-10-20", row)
    with pytest.raises(JournalFormatError, match=f"^рядок 3: .*{message}"):
        import_journal(group, path)


def test_failed_import_changes_nothing(group, write_journal):
    before = [(s.id, len(s.grades)) for s in group]
    path = write_journal(
        "1;Вебтехнології;91;2026-10-20", "2;Вебтехнології;105;2026-10-20"
    )

    with pytest.raises(JournalFormatError):
        import_journal(group, path)

    assert [(s.id, len(s.grades)) for s in group] == before


def test_wrong_header_is_rejected(write_journal):
    path = write_journal(header="id;course;score;date")
    with pytest.raises(JournalFormatError, match="заголовок"):
        list(read_rows(path))


def test_read_rows_opens_file_lazily(tmp_path):
    rows = read_rows(tmp_path / "missing.csv")  # файлу немає, але помилки ще немає

    with pytest.raises(StorageError, match="не знайдено"):
        next(rows)


def test_parse_entries_keeps_line_numbers(write_journal):
    path = write_journal("1;Python;91;2026-10-20", "2;Python;67;2026-10-20")
    assert [e.line for e in parse_entries(read_rows(path))] == [2, 3]
