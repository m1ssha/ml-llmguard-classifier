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

## End-to-end обучение и экспорт prompt injection модели

Для одного запуска полного цикла (загрузка HF-датасета, обучение stronger encoder, экспорт inference bundle и отчёта) используйте скрипт:

[`classifier/scripts/run_prompt_injection_train_export.py`](classifier/scripts/run_prompt_injection_train_export.py)

Пример запуска:

```bash
python -m classifier.scripts.run_prompt_injection_train_export \
  --dataset-id neuralchemy/Prompt-injection-dataset \
  --output-root classifier/artifacts \
  --seed 42 \
  --experiment-name prompt_injection_e2e \
  --include-baseline true \
  --profile balanced
```

Ключевые параметры:
- `--dataset-id` — id датасета Hugging Face (по умолчанию `neuralchemy/Prompt-injection-dataset`)
- `--output-root` — корневая директория артефактов (по умолчанию `classifier/artifacts`)
- `--seed` — seed воспроизводимости (по умолчанию `42`)
- `--experiment-name` — имя эксперимента
- `--include-baseline` — включить baseline-модель в отчёт (`true/false`)
- `--profile` — профиль порогов (`balanced` или `high_recall_security`)

Скрипт сохраняет inference-ready bundle с обязательными файлами:
`encoder_model.joblib`, `tokenizer.joblib`, `label_mapping.json`, `thresholds.json`,
`training_metadata.json`, `artifact_manifest.json`, `evaluation_report.json`.
