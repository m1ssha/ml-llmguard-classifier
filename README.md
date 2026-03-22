# ML LLMGuard Classifier

Репозиторий хранит артефакты OpenSpec и кодовую базу MVP-классификатора атак на LLM.

## Что хранится в репозитории

### 1) Спецификации и OpenSpec-артефакты
- Базовая спецификация: [`openspec_classifier_spec.md`](openspec_classifier_spec.md)
- Конфиг OpenSpec: [`openspec/config.yaml`](openspec/config.yaml)
- Активный change: [`openspec/changes/plan-openspec-classifier/`](openspec/changes/plan-openspec-classifier/)
  - proposal: [`openspec/changes/plan-openspec-classifier/proposal.md`](openspec/changes/plan-openspec-classifier/proposal.md)
  - design: [`openspec/changes/plan-openspec-classifier/design.md`](openspec/changes/plan-openspec-classifier/design.md)
  - tasks: [`openspec/changes/plan-openspec-classifier/tasks.md`](openspec/changes/plan-openspec-classifier/tasks.md)
  - capability specs: [`openspec/changes/plan-openspec-classifier/specs/`](openspec/changes/plan-openspec-classifier/specs/)

### 2) Код классификатора
- Пакет: [`classifier/`](classifier/)
- Исходники: [`classifier/src/`](classifier/src/)
  - dataset: [`classifier/src/dataset/`](classifier/src/dataset/)
  - models: [`classifier/src/models/`](classifier/src/models/)
  - training: [`classifier/src/training/`](classifier/src/training/)
  - inference: [`classifier/src/inference/`](classifier/src/inference/)
  - evaluation: [`classifier/src/evaluation/`](classifier/src/evaluation/)
  - api: [`classifier/src/api/`](classifier/src/api/)
  - common: [`classifier/src/common/`](classifier/src/common/)

### 3) Данные, конфиги, тесты и отчёты
- Данные: [`classifier/data/`](classifier/data/)
- Конфиги: [`classifier/configs/`](classifier/configs/)
- Скрипты: [`classifier/scripts/`](classifier/scripts/)
- Тесты: [`classifier/tests/`](classifier/tests/)
- Отчёты: [`classifier/reports/`](classifier/reports/)

### 4) Зависимости
- Список Python-зависимостей: [`requirements.txt`](requirements.txt)
