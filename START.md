# Старт з ЛР 6 для нових студентів

Ця гілка - стан репозиторію `student-portal` після ЛР 5: модель предметної області (ЛР 2), декоратори, генератори й асинхронний імпорт (ЛР 3), тести pytest (ЛР 4), mock-об’єкти, покриття і GitHub Actions (ЛР 5). З неї можна одразу починати ЛР 6, не виконуючи попередніх робіт. Про зарахування ЛР 1–5 домовтеся з викладачем.

## 1. Власний репозиторій

На GitHub створіть **порожній** публічний репозиторій `student-portal`: без README, `.gitignore` і ліцензії. Потім:

```bash
git clone --branch lab6-start --single-branch https://github.com/vitalii-cs-vnu/cs-f3-webdev-labs.git student-portal
cd student-portal
git branch -m main
git rm -q START.md
git commit -m "chore: стартовий стан після ЛР 5"
git remote set-url origin https://github.com/<ваш-логін>/student-portal.git
git push -u origin main
git tag -a v0.5.0 -m "Стартовий стан після ЛР 5"
git push origin v0.5.0
```

Історія комітів викладача залишається в репозиторії: з неї видно, де починається ваша робота.

## 2. Перевірка

```bash
uv sync
uv run pytest --cov
```

Очікуваний результат - 95 тестів пройдено, покриття не нижче 90 %. На GitHub у вкладці **Actions** перевірки `checks` і `tests` для `main` мають бути зеленими.

## 3. Налаштування з ЛР 1, потрібні для ЛР 6

Виконайте за ЛР 1 (у Moodle):

- завдання 2, п. 7 - додайте партнера співавтором (**Settings → Collaborators**): він рецензуватиме ваші pull request;
- завдання 3, пп. 1–4 - створіть дошку GitHub Projects `student-portal: розробка` зі стовпцями `Backlog`, `Ready`, `In progress`, `In review`, `Done` і полями `Priority`, `Lab`, `Sprint`;
- завдання 6, п. 1 - увімкніть ruleset `protect-main`. Робіть це **після** `git push` з розділу 1: потім прямі push у `main` заборонено, зміни потрапляють туди лише через pull request.

## 4. Далі

Відкрийте ЛР 6 і почніть із завдання 1. Розділ README «Перевірки» і «Тести» описує команди, якими користуються всі наступні роботи.
