import inspect

import pytest

from student_portal.exceptions import (
    DuplicateStudentError,
    InvalidGradeError,
    StudentNotFoundError,
)
from student_portal.grades import Grade
from student_portal.group import Group
from student_portal.people import Student


def test_len_and_iteration_follow_insertion_order(group):
    assert len(group) == 3
    assert [s.id for s in group] == [1, 2, 3]


def test_add_rejects_duplicate_id(group):
    with pytest.raises(DuplicateStudentError, match="id=1"):
        group.add(Student(1, "Інна", "Коваль"))
    assert len(group) == 3


def test_get_unknown_student_raises(group):
    with pytest.raises(StudentNotFoundError, match="id=42"):
        group.get(42)


def test_remove_returns_student_and_deletes_it(group):
    removed = group.remove(2)

    assert removed.last_name == "Мельник"
    assert [s.id for s in group] == [1, 3]


@pytest.mark.parametrize(
    ("ids", "expected"),
    [([], 1), ([1, 2, 3], 4), ([1, 7], 8)],
    ids=["empty", "consecutive", "gap"],
)
def test_next_id_follows_max_id(ids, expected):
    group = Group("КН-12")
    for student_id in ids:
        group.add(Student(student_id, "Студент", f"Прізвище{student_id}"))
    assert group.next_id() == expected


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        pytest.param("Коваль", ["Коваль"], id="exact"),
        pytest.param("коваль", ["Коваль"], id="lowercase"),
        pytest.param("  Мельник ", ["Мельник"], id="spaces"),
        pytest.param("ко", ["Коваль", "Бойко"], id="substring"),
        pytest.param("Шевчук", [], id="not-found"),
    ],
)
def test_find_by_last_name(group, query, expected):
    assert [s.last_name for s in group.find(query)] == expected


def test_ranking_puts_best_first_and_ungraded_last(group):
    assert [s.last_name for s in group.ranking()] == ["Коваль", "Мельник", "Бойко"]


def test_ranking_breaks_ties_by_last_name(make_student):
    group = Group("КН-12")
    for student in (make_student("Шевчук", 80), make_student("Бондар", 80)):
        group.add(student)
    assert [s.last_name for s in group.ranking()] == ["Бондар", "Шевчук"]


def test_group_average_skips_students_without_grades(group):
    assert group.average() == pytest.approx((91.5 + 61) / 2)


def test_empty_group_has_no_average():
    assert Group("КН-12").average() is None


def test_iter_grades_is_generator_of_pairs(group):
    pairs = group.iter_grades()

    assert inspect.isgenerator(pairs)
    assert [(s.id, g.score) for s, g in pairs] == [(1, 95), (1, 88), (2, 61)]


def test_courses(group):
    assert group.courses() == {"Python", "Git"}


def test_ects_distribution_keeps_scale_order(group):
    distribution = group.ects_distribution()

    assert distribution == {"A": 1, "B": 1, "E": 1}
    assert list(distribution) == ["A", "B", "E"]


def test_transaction_keeps_changes_without_error(group):
    with group.transaction():
        group.get(3).add_grade(Grade("Python", 70))

    assert group.get(3).average() == 70


def test_transaction_restores_group_after_error(group):
    before = [(s.id, s.average()) for s in group]

    with pytest.raises(InvalidGradeError), group.transaction():
        group.remove(2)
        group.get(3).add_grade(Grade("Python", 70))
        group.get(1).add_grade(Grade("Python", 105))

    assert [(s.id, s.average()) for s in group] == before
