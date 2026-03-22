## Why

Текущий пайплайн даёт сильный MVP по prompt injection, но для диплома не хватает доказательной ширины: нужна внятная мультидатасетная стратегия, сравнимые эксперименты между источниками и формализованный протокол оценки обобщающей способности. Добавление датасета Anthropic/hh-rlhf (поля chosen/rejected) позволит расширить покрытие benign/unsafe-подобных сценариев и снизить риск переобучения на одном источнике.

## What Changes

- Добавить мультидатасетный протокол обучения с раздельной ролью источников:
  - prompt-injection-датасет как основной источник атакующих паттернов;
  - hh-rlhf как источник сложных benign/assistant-alignment примеров и негативных пар.
- Ввести унифицированный слой маппинга схемы колонок для разнородных HF-датасетов (включая chosen/rejected).
- Добавить стратегию сборки train/validation/test с контролем leakage между датасетами и обязательной трассировкой source-domain.
- Расширить протокол экспериментов для диплома:
  - single-dataset vs multi-dataset;
  - cross-dataset generalization;
  - ablation по источникам данных.
- Зафиксировать артефакты воспроизводимости для диплома: конфиги микса, версии датасетов, отчёты по срезам и итоговые таблицы.

## Capabilities

### New Capabilities
- `multidataset-training-protocol`: протокол смешивания нескольких датасетов (role-based composition, split policy, source-aware evaluation).
- `cross-dataset-evaluation-for-diploma`: обязательные эксперименты на переносимость и устойчивость между разными источниками данных.

### Modified Capabilities
- `hf-dataset-flexible-loading`: расширение требований на поддержку схемы chosen/rejected и source-aware нормализации.
- `classifier-dataset-and-labeling`: добавление требований к source-domain тегам, mix policy и anti-leakage split constraints.
- `classifier-training-and-evaluation`: добавление требований к multi-dataset экспериментам и cross-dataset отчётности.

## Impact

- Affected code:
  - dataset loading/normalization;
  - training pipelines;
  - experiment runner и отчёты.
- Affected artifacts:
  - новые capability specs;
  - обновление существующих specs и tasks.
- Dependencies/systems:
  - Hugging Face datasets API (дополнительный источник Anthropic/hh-rlhf);
  - расширенные отчёты для дипломной главы по экспериментам.
