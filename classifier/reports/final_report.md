# Итоговый отчёт MVP-классификатора

## Что реализовано

- Датасетный фундамент: структура `classifier/data/{raw,processed}`, схема полей и валидаторы категорий/языков.
- Quality checks: контроль shortcut-паттернов с блокировкой обучения при нарушении порогов.
- Два пайплайна обучения: baseline (`TF-IDF + Logistic Regression`) и encoder-like CPU-friendly pipeline.
- Единый preprocessing для train/inference.
- Reproducibility controls: seed, snapshot конфигурации, versioned experiment output dirs.
- Двухэтапный inference: binary stage и условный threat stage.
- Rule-based сигналы: prompt leakage, role override, bypass, obfuscation.
- Единый `predict(text)`-контракт с JSON-валидацией полей и audit-логированием confidences/signals.
- Оценка и протокол экспериментов: baseline-vs-encoder, binary-only-vs-two-stage, rule-ablation.
- CPU smoke/performance тест и integration layer для gateway/backend.

## Ограничения

- Encoder pipeline в MVP реализован как лёгкий surrogate для CPU-first сценария.
- Метрики и эксперименты ориентированы на структурную воспроизводимость и требуют заполненного production-датасета.

## Риски

- Дрейф распределений классов/языков в реальном трафике.
- Возможность новых обфускаций, не покрытых эвристиками.

## Направления развития

- Переход на настоящий transformer encoder с калибровкой confidence.
- Расширение rule layer и session-aware фичей.
- Добавление интеграционных e2e-тестов с backend gateway.

## Соответствие DoD

- Все задачи change отмечены выполненными.
- Доступны проверяемые артефакты: код модулей, конфиги, тесты и отчёт.

