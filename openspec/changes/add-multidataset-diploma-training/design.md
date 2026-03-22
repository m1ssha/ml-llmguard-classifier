## Context

Проект имеет рабочий MVP-пайплайн вокруг prompt injection, но дипломная задача требует более широкого и методологически корректного исследования: доказать устойчивость классификатора не на одном датасете, а на нескольких источниках с разными распределениями. Пользователь дополнительно указал использование Anthropic/hh-rlhf с колонками chosen/rejected как важного источника для расширения покрытия.

Текущее состояние:
- есть инфраструктура загрузки HF-датасетов и нормализации схемы;
- есть train/export pipeline для prompt injection;
- есть отчёты по базовым метрикам и robustness-срезам.

Ограничения:
- нельзя смешивать датасеты «в лоб» без source-domain контроля;
- нужно избежать data leakage между источниками и срезами;
- протокол должен быть воспроизводим и прозрачен для дипломной защиты.

## Goals / Non-Goals

**Goals:**
- Ввести единый мультидатасетный ingestion-слой с поддержкой `chosen/rejected` и источниковых меток.
- Определить формальный протокол построения датасета для двухэтапной классификации (binary + threat stage).
- Ввести обязательные cross-dataset эксперименты для демонстрации обобщаемости.
- Зафиксировать структуру выходных артефактов, пригодных для дипломной главы с результатами.

**Non-Goals:**
- Полная production-интеграция в gateway runtime.
- Online-learning и session-aware multi-turn inference.
- Немедленный переход на тяжёлые transformer-модели в этом change.

## Decisions

1. Decision: Роль датасетов разделяется, а не объединяется без контекста.
- Prompt-injection датасет используется как основной источник явных атаковых примеров и threat-разметки.
- Anthropic/hh-rlhf используется как источник сложных benign/alignment и пар сравнений chosen/rejected для построения hard-negative и robustness-срезов.
- Rationale: это снижает риск «подгонки» под один датасет и добавляет реалистичные безопасные/пограничные формулировки.
- Alternative considered: обучать только на prompt-injection датасете. Отвергнуто, т.к. слабее для дипломной демонстрации обобщения.

2. Decision: Ввести source-aware canonical schema до этапа split.
- Каждый пример приводится к канонической структуре: id, text, binary_label, threat_type, language, source, dataset_id, split_role.
- Для hh-rlhf:
  - chosen трактуется как преимущественно benign-aligned сигнал;
  - rejected используется как кандидат в unsafe/контрастный негатив после фильтрации по правилам и/или weak labeling.
- Rationale: единый интерфейс упрощает сравнение моделей и контроль leakage.
- Alternative considered: dataset-specific пайплайны без канонизации. Отвергнуто из-за сложной трассируемости и слабой воспроизводимости.

3. Decision: Разделение экспериментов на три уровня.
- Level A: single-dataset baseline (prompt-injection only).
- Level B: mixed training (prompt-injection + hh-rlhf-derived samples).
- Level C: cross-dataset transfer (train на одном/миксе, test на другом домене).
- Rationale: структура экспериментов напрямую отвечает на дипломный вопрос «что даёт мультидатасетный подход».
- Alternative considered: один итоговый mixed run. Отвергнуто, т.к. нет причинно-понятного сравнения.

4. Decision: Обязательные отчёты включают не только aggregate метрики, но и source-slice анализ.
- Метрики: binary и multiclass (где применимо), плюс per-source FP/FN.
- Добавить отчётные таблицы: contribution каждого датасета, robustness по срезам obfuscation/policy_bypass/multilingual/benign_security_discussion.
- Rationale: это делает защиту диплома убедительной и проверяемой.

5. Decision: Конфигурация эксперимента задаётся явно (dataset mix config).
- Конфиг описывает: источники, веса/квоты, mapping-правила, split strategy, seed, активный профиль порогов.
- Все артефакты прогона сохраняют этот конфиг и версии датасетных источников.
- Rationale: воспроизводимость и аудитируемость.

## Risks / Trade-offs

- [Risk] Некорректная интерпретация hh-rlhf chosen/rejected как безопасный/опасный сигнал. → Mitigation: явный weak-labeling protocol + ручная валидация поднабора + отчёт о шуме меток.
- [Risk] Data leakage при смешивании источников. → Mitigation: source-aware split, hash-based dedup и проверка near-duplicate между train/test.
- [Risk] Улучшение aggregate-метрик ценой роста FP на benign-security обсуждениях. → Mitigation: отдельный benign_security_discussion slice и обязательный FP-анализ.
- [Risk] Избыточная сложность для сроков диплома. → Mitigation: staged rollout (A→B→C), где каждый уровень самодостаточен и приносит полезный результат.
- [Risk] Сильная зависимость от внешних HF-датасетов. → Mitigation: фиксировать revision/metadata, сохранять snapshots и manifest артефактов.

## Migration Plan

1. Добавить capability-спеки для мультидатасетного протокола и cross-dataset оценки.
2. Расширить существующие спек-области (loader, dataset schema, training/eval) под source-aware flow.
3. Реализовать конфиг микса датасетов и адаптер для hh-rlhf chosen/rejected.
4. Обновить train/eval скрипты на staged экспериментальный режим (A/B/C).
5. Обновить отчёты и шаблон финальных дипломных таблиц.
6. Провести контрольный прогон и зафиксировать артефакты в reproducibility bundle.

Rollback strategy:
- сохранить текущий single-dataset pipeline как fallback-профиль;
- переключение режимов через конфиг без удаления существующих сценариев.

## Open Questions

- Какие правила weak labeling для rejected будут приняты как базовые в дипломе?
- Нужен ли отдельный human-labeled validation subset для hh-rlhf-derived части?
- Какая минимальная доля hh-rlhf в mixed train допустима без деградации threat-stage?
- Будет ли threat taxonomy расширяться сразу, или сначала закрепляется binary-generalization эффект?