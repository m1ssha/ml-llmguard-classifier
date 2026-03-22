# AGENTS

Документ определяет роли агентной разработки для проекта классификатора атак на LLM.

## Общие правила

- Источник требований: [`openspec_classifier_spec.md`](openspec_classifier_spec.md).
- Рабочий change для реализации: [`openspec/changes/plan-openspec-classifier/`](openspec/changes/plan-openspec-classifier/).
- Порядок выполнения задач: строго по [`tasks.md`](openspec/changes/plan-openspec-classifier/tasks.md).
- Любые изменения требований фиксируются через OpenSpec-артефакты, а не «мимо» процесса.

## Роли агентов

### 1) Orchestrator Agent
**Ответственность:** декомпозиция, приоритизация, контроль зависимостей между агентами.

**Входы:** [`proposal.md`](openspec/changes/plan-openspec-classifier/proposal.md), [`design.md`](openspec/changes/plan-openspec-classifier/design.md), [`tasks.md`](openspec/changes/plan-openspec-classifier/tasks.md).

**Выходы:** актуализированный план выполнения и статус по этапам.

### 2) Data Agent
**Ответственность:** датасет, разметка, quality checks.

**Опирается на:** [`specs/classifier-dataset-and-labeling/spec.md`](openspec/changes/plan-openspec-classifier/specs/classifier-dataset-and-labeling/spec.md).

**Ключевые артефакты:** схема полей, валидация категорий/языков, проверки shortcut-паттернов.

### 3) Modeling Agent
**Ответственность:** baseline + encoder-based обучение, сохранение артефактов моделей.

**Опирается на:** [`specs/classifier-training-and-evaluation/spec.md`](openspec/changes/plan-openspec-classifier/specs/classifier-training-and-evaluation/spec.md).

**Ключевые артефакты:** reproducible training pipelines, метрики, отчёты экспериментов.

### 4) Inference Agent
**Ответственность:** двухэтапный inference flow и API-контракт для backend.

**Опирается на:**
- [`specs/llm-attack-classifier-mvp/spec.md`](openspec/changes/plan-openspec-classifier/specs/llm-attack-classifier-mvp/spec.md)
- [`specs/classifier-inference-interface/spec.md`](openspec/changes/plan-openspec-classifier/specs/classifier-inference-interface/spec.md)

**Ключевые артефакты:** единый `predict(text)`, JSON-ответ, логирование confidence/signal.

### 5) Rules/Security Agent
**Ответственность:** rule-based сигналы и их интеграция с ML-оценкой.

**Опирается на:** [`design.md`](openspec/changes/plan-openspec-classifier/design.md).

**Ключевые артефакты:** эвристики (role override, prompt leakage, bypass, obfuscation), объяснимые сигналы.

### 6) Evaluation Agent
**Ответственность:** метрики и экспериментальный протокол.

**Опирается на:** [`specs/classifier-training-and-evaluation/spec.md`](openspec/changes/plan-openspec-classifier/specs/classifier-training-and-evaluation/spec.md).

**Ключевые артефакты:** baseline-vs-encoder, binary-vs-two-stage, rule-ablation.

### 7) Integration Agent
**Ответственность:** интеграция с backend/gateway и проверка совместимости контракта.

**Опирается на:** [`specs/classifier-inference-interface/spec.md`](openspec/changes/plan-openspec-classifier/specs/classifier-inference-interface/spec.md).

**Ключевые артефакты:** стабильный интерфейс вызова, обработка ошибок, интеграционные тесты.

## Правила взаимодействия

1. Data Agent завершает минимально валидный датасет до старта полного обучения.
2. Modeling Agent и Rules/Security Agent синхронизируют формат признаков для inference.
3. Inference Agent не меняет контракт без согласования с Integration Agent.
4. Evaluation Agent блокирует релиз при отсутствии обязательных метрик/экспериментов.
5. Orchestrator Agent финализирует статус этапа только при выполнении DoD из спецификации.

## Критерии готовности агентного цикла

Этап считается завершённым, если:
- задачи соответствующего блока в [`tasks.md`](openspec/changes/plan-openspec-classifier/tasks.md) закрыты;
- результаты проверяемы (отчёты, метрики, артефакты моделей, API-контракт);
- нет критических расхождений с OpenSpec-спеками.
