import asyncio

import pytest

from student_portal import notify
from student_portal.notify import notify_all, notify_sequentially, send_result


@pytest.fixture(autouse=True)
def no_delay(monkeypatch):
    """Тести не чекають «поштовий сервер»."""
    monkeypatch.setattr(notify, "SEND_DELAY", 0)


def test_send_result_reports_average(group):
    message = asyncio.run(send_result(group.get(1)))
    assert message == "Коваль Олена: середній бал 91.5"


def test_send_result_without_grades(group):
    assert asyncio.run(send_result(group.get(3))) == "Бойко Ірина: оцінок немає"


def test_notify_sequentially_keeps_order(group):
    messages = asyncio.run(notify_sequentially(group))
    assert [m.split(":")[0] for m in messages] == [
        "Коваль Олена",
        "Мельник Андрій",
        "Бойко Ірина",
    ]


@pytest.mark.parametrize("limit", [1, 2, 3])
def test_notify_all_respects_limit_and_order(mocker, group, limit):
    active = 0
    peak = 0

    async def fake_send(student):
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0.01)
        active -= 1
        return student.last_name

    send = mocker.patch("student_portal.notify.send_result", side_effect=fake_send)

    messages = asyncio.run(notify_all(group, limit=limit))

    assert messages == ["Коваль", "Мельник", "Бойко"]
    assert peak == limit
    assert send.await_count == 3
