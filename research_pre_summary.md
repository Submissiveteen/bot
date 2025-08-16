S0 — Инициализация и рамки анализа
Что делали: зафиксировали входы, ветки/ветку по умолчанию, цели, источники; обозначили формат ссылок и этапность.

Ключевые решения:

[Decision] Анализируем default branch и фиксируем SHA последнего коммита в отчёте; далее — этапная подача результатов. [Assumption] Это снижает риск расхождений с текущим состоянием кода. [Res1.md §Инициализация]

[Decision] Источники для каждого факта — обязательны; где нет источника — пометка [Unverified]. [Mod2.md §Формат; Roadmap]

На что опирались: входные 5 файлов и репозиторий; требования к ссылочной дисциплине. [Mod1.md §Введение], [Mod2.md §Дорожная карта S0–S7], [Mod3.md §Приоритеты/Fail-closed], [Res1.md §bot vs core], [Res2.md §Аудит]

S1 — Инвентаризационный аудит репозитория
Что делали: составили карту проекта (path/type/loc/last_commit/findings), прошлись по bot/, core/, data/|config/, env/CI.

Ключевые находки (сводка):

[Evidence] Дубли/коллизии FSM и /start; отсутствие строгой валидации суммы/кошелька. [Res2.md §UX-воронка; дубли; валидация]

[Evidence] Незавершённые _load_data/_load_weights; генерация deeplink через небезопасную подстановку; подпись по стратегиям частично. [Res1.md §Статич. vs динамич. скоринг; deeplink]

[Evidence] Fail-open в KYC/лимитах; substring-match агрегаторов; нет canonical IDs. [Mod1.md §A–C], [Mod3.md §1–3]

Решения:

[Decision] Вынести конфигурации/схемы в YAML/CSV, всё грузить через валидатор; без схемы — fail-fast. [Mod3.md §Строгая схема], [Mod2.md §S1 Data Integrity]

[Decision] Canonical aggregator IDs + строгий матч, никакого substring. [Mod3.md §Явное сопоставление]

S2 — Нормализация входных рекомендаций (Mod1/2/3, Res1/2)
Что делали: распилили предложения на атомарные задачи и разнесли по таксономии (Безопасность/Данные/UX/Архитектура/CI/Лояльность).

Ключевые кластеры:

Безопасность/Данные: fail-closed проверки, строгие схемы, защита секретов, canonical IDs. [Mod3.md §1–4], [Mod2.md §S0–S1]

UX: убрать дубли, обязательный ввод, дружелюбные ошибки, FSM-дерево. [Mod1.md §C], [Res2.md §UX-аудит]

Скоринг/KYC: заменить статические таблицы на динамический расчёт; Decline Index; пороги KYC из данных. [Mod1.md §A/D], [Res1.md §Статич. vs динамич.]

CI: schema-guards, линтеры, coverage, Actions. [Mod2.md §S4]

Решения: [Decision] Приняли почти все предложения, часть — модифицированы (например, глубина FSM/микросервисы — позже). [Mod1.md §2; §Этапы], [Res2.md §Самокритика/разрыв потока]

S3 — Диагностика критичности (Impact × Effort × Freshness)
Что делали: оценили каждую проблему по влиянию на безопасность сделок/конверсию/затраты внедрения/риску «устаревших данных».

Результат (верхний ряд):

[Decision] S0–S1 первыми: env-валидация, защита секретов, fail-closed, схемы, canonical IDs. [Mod2.md §S0], [Mod3.md §1–4]

[Decision] S2: UX-жёсткость (обязательные поля, устранение дублей, явные ошибки). [Res2.md §UX-воронка]

[Decision] S3: динамический скоринг + Decline Index + KYC-логика (исправить fail-open). [Mod1.md §A/D], [Mod3.md §1], [Res1.md §Статич./динамич.]

S4 — Бенчмаркинг best practices (точечно)
Что делали: сопоставили предложения с практиками: fail-closed, schema-as-code, конфигурации вне кода, безопасные шаблоны (Jinja2), CI guards.

Решения:

[Decision] Заменить строковую подстановку шаблонов на Jinja2 + StrictUndefined (ошибка на пропуски) — fail-closed by design. [Mod1.md §Deeplink], [Mod3.md §Deeplink улучшения]

[Decision] Schema-валидация при загрузке любых CSV/YAML; при расхождении — блокировка. [Mod3.md §Строгая схема]

S5 — Целевая архитектура (To-Be)
Что делали: спроектировали слои App(bot) / Domain(core) / Data / Infra / CI, внешние конфиги, валидаторы схем, скоринг с весами, KYC thresholds, локализация.

Ключевые элементы:

Разделение bot vs core; Selector/Engine/Deeplink как доменные сервисы; данные вне кода. [Res1.md §bot vs core]

Fail-closed guard на селектор/KYC; canonical IDs; Decline Index в скоринге; локализация сообщений. [Mod1.md §A–D], [Mod3.md §1–6], [Res2.md §UX]

Решения: [Decision] Схемы и конфиги как единый источник правды; тесты-сторожи (schema guards) в CI. [Mod2.md §S4]

S6 — Приоритизированный Roadmap (фазы S0…S6)
Что делали: собрали фазовый план с DoD, зависимостями, приоритетами; вывели таблицу-дорожную карту.

Опорные решения/приоритеты:

S0 Stabilize & Secure: env-валидация, секреты, fail-closed, базовая input-валидация. [Mod2.md §S0], [Mod3.md §1–5]

S1 Data Integrity: схемы CSV/YAML, canonical IDs, _load_data, блок на расхождениях. [Mod3.md §2–3], [Mod2.md §S1]

S2 UX Hardening: обязательный ввод суммы/кошелька, убрать дубли, упрощение nationality/residence, дружелюбные ошибки. [Res2.md §UX-воронка], [Mod1.md §C]

S3 Dynamic Scoring & KYC: динамический скоринг (fee/decline/kyc_threshold), интеграция Decline Index; фикс fail-open. [Mod1.md §A/D], [Res1.md §Статич./динамич.]

S4 CI/CD & Testing: unit+e2e, schema guards, secrets scan, Actions + coverage. [Mod2.md §S4]

S5 Localization & Growth: мультиязычность, новые агрегаторы/страны, мониторинг/алёртинг. [Mod3.md §5–6]

S7 — Кодогенерация (патчи/новые файлы)
Что делали: сгенерировали diff-патчи и новые файлы для S0–S6: безопасный DeeplinkBuilder (Jinja2), fail-closed guards, схемы/конфиги, CI-workflow, валидаторы.

Главные артефакты:

core/schema_validator.py — базовая валидация суммы/кошелька. [Decision] Fail-closed при ошибке ввода. [Mod2.md §S0], [Res2.md §Валидация]

config/aggregators.yml, config/weights.yml, config/cluster_map.yml — конфиги вне кода; загрузка через _load_data/_load_weights с проверкой. [Mod3.md §Строгая схема/ID]

Переписан DeeplinkBuilder на Jinja2 + StrictUndefined; исключения вместо «тихих» подстановок. [Mod1.md §Deeplink], [Mod3.md §Deeplink улучшения]

KYC guard по Tier-порогам (fail-closed при недостаточном уровне). [Res2.md §KYC-логика]

.github/workflows/ci.yml — pytest + (дальше) линтер/coverage; .env.example — только примеры, без секретов. [Mod2.md §S4; §Secure Secrets], [Mod3.md §Защита секретов]

Замечание: пуш/PR не выполнялись автоматически (нет прямого git-доступа из чата), но контент PR собран. [Decision] PR делается одной CLI-командой/Action (см. инструкции в переписке). [Assumption]

S8 — Доказательная матрица решений
Что делали: свели все рекомендации в таблицу: Источник → Обоснование → Статус (Принято/Изменено/Отклонено) → Комментарий, отсортировав по фазам Roadmap.

Примеры строк:

Fail-Closed Checks — [Evidence] безопасность выше доступности; при сбое не пропускаем транзакцию. Статус: Принято. [Mod3.md §1]

Строгие схемы CSV/YAML — [Evidence] без схем — расхождения/ломкость; Статус: Принято. [Mod3.md §2], [Mod2.md §S1]

Canonical aggregator IDs — [Evidence] исключает коллизии/substring-match; Статус: Принято. [Mod3.md §3]

Jinja2 вместо string.replace — [Evidence] исключает silent-баги в шаблонах; Статус: Принято. [Mod1.md §Deeplink], [Mod3.md §Deeplink улучшения]

Два шага nationality/residence — [Conflict] дублирующий сбор; Статус: Изменено (объединить/сократить). [Res2.md §UX-воронка]

S9 — Финальный Pull Request на основе Roadmap
Описанные этапы:

Создание новой ветки и включение изменений

Подготовка описания Pull Request

Чеклист этапов S0–S6

Pre-merge Checklist

Ссылки на источники изменений
