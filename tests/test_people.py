import pytest

from student_portal.grades import Grade
from student_portal.people import Person, Student, Teacher


def test_full_name_starts_with_last_name():
    assert Student(1, "Олена", "Коваль").full_name == "Коваль Олена"


@pytest.mark.parametrize(
    ("person", "expected"),
    [
        (Student(1, "Олена", "Коваль"), "Коваль Олена (студент)"),
        (Teacher(2, "Петро", "Іваненко", ["Python"]), "Іваненко Петро (викладач)"),
    ],
    ids=["student", "teacher"],
)
def test_str_shows_name_and_role(person, expected):
    assert str(person) == expected


def test_person_is_abstract():
    with pytest.raises(TypeError):
        Person(1, "Олена", "Коваль")  # type: ignore[abstract]


def test_student_without_grades_has_no_average(make_student):
    assert make_student("Бойко").average() is None


def test_average_of_grades(make_student):
    assert make_student("Коваль", 95, 88).average() == pytest.approx(91.5)


def test_add_grade_changes_average(make_student):
    student = make_student("Коваль", 90)

    student.add_grade(Grade("Git", 80))

    assert student.average() == 85


def test_grades_for_returns_only_that_course():
    student = Student(1, "Олена", "Коваль", [Grade("Python", 95), Grade("Git", 88)])
    assert [g.score for g in student.grades_for("Git")] == [88]
