# ML LLMGuard Classifier

Репозиторий для проектирования и поэтапной реализации MVP-классификатора атак на LLM в составе Security Gateway.

## Что в проекте сейчас

- Исходная постановка задачи: [`openspec_classifier_spec.md`](openspec_classifier_spec.md)
- OpenSpec-конфиг: [`openspec/config.yaml`](openspec/config.yaml)
- Подготовленный change с полным набором артефактов:
  - [`openspec/changes/plan-openspec-classifier/proposal.md`](openspec/changes/plan-openspec-classifier/proposal.md)
  - [`openspec/changes/plan-openspec-classifier/design.md`](openspec/changes/plan-openspec-classifier/design.md)
  - [`openspec/changes/plan-openspec-classifier/tasks.md`](openspec/changes/plan-openspec-classifier/tasks.md)
  - спецификации capabilities в [`openspec/changes/plan-openspec-classifier/specs/`](openspec/changes/plan-openspec-classifier/specs/)

## Цель MVP

Собрать рабочий модуль, который:
1. Определяет, вредоносный ли запрос (`benign`/`malicious`);
2. Для вредоносных запросов определяет тип угрозы;
3. Возвращает унифицированный результат инференса для интеграции в backend/gateway.

## Ключевые требования (сводно)

- Двухэтапная классификация: binary + threat type;
- Гибридная логика: ML-предсказание + rule-based сигналы;
- Baseline (TF-IDF + Logistic Regression) и encoder-based модель;
- Обязательные метрики качества и экспериментальный протокол;
- CPU-friendly инференс и воспроизводимость обучения.

## Как продолжить работу

1. Перейти к реализации задач из [`tasks.md`](openspec/changes/plan-openspec-classifier/tasks.md);
2. Запустить workflow применения change через команду `/opsx:apply`;
3. Реализовывать пункты последовательно по разделам 1→5.

## Планируемая структура модуля (ориентир)

```text
classifier/
  data/
    raw/
    processed/
  notebooks/
  src/
    dataset/
    features/
    models/
    training/
    inference/
    evaluation/
    api/
  tests/
  configs/
```

## Статус

- OpenSpec-артефакты для MVP: готовы (proposal/design/specs/tasks).
- Кодовая реализация классификатора: в работе (следующий этап — `/opsx:apply`).
