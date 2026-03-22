## Why

Текущий проект уже содержит разрозненные элементы загрузки датасета, обучения, оценки и инференса, но отсутствует единый production-oriented entrypoint для полного цикла подготовки артефактов под prompt injection кейс. Нужен один воспроизводимый запуск, который снижает операционные риски интеграции и ускоряет выпуск моделей в inference-контур.

## What Changes

- Добавляется новый CLI-скрипт `classifier/scripts/run_prompt_injection_train_export.py` для end-to-end пайплайна: загрузка HF датасета, нормализация схемы/лейблов, формирование проектных samples, обучение encoder-пайплайна, экспорт inference bundle, сохранение отчётов и manifest.
- Добавляется поддержка CLI-аргументов: `dataset_id` (default `neuralchemy/Prompt-injection-dataset`), `output_root` (default `classifier/artifacts`), `seed` (default `42`), `experiment_name`, `include_baseline` (true/false), `profile` (`balanced` или `high_recall_security`).
- Добавляется alias-логика колонок с понятными ошибками при невозможности сопоставить обязательные поля датасета.
- Добавляется генерация обязательного набора артефактов: `encoder_model.joblib`, `tokenizer.joblib`, `label_mapping.json`, `thresholds.json`, `training_metadata.json`, `artifact_manifest.json`, `evaluation_report.json`.
- Добавляется отчёт с бинарными метриками для профилей `balanced` и `high_recall_security`, robustness slices и путями к экспортированным артефактам.
- Добавляются тесты в `classifier/tests/`: smoke-тест запуска и проверка структуры артефактного bundle.
- Добавляется краткая документация запуска в `README.md`.

## Capabilities

### New Capabilities
- `prompt-injection-train-export-pipeline`: единый воспроизводимый процесс обучения и экспорта inference-совместимого bundle из HF prompt injection датасета.
- `prompt-injection-artifact-bundle-contract`: стабильный контракт состава артефактов и evaluation-отчёта, пригодный для загрузки inference-слоем без обращения к training internals.

### Modified Capabilities
- None.

## Impact

- Затронутый код: `classifier/scripts/`, `classifier/src/dataset/`, `classifier/src/training/`, `classifier/src/models/`, `classifier/src/evaluation/`, `classifier/tests/`, `README.md`.
- Интеграционный эффект: упрощение передачи результатов обучения в inference через стандартизированный manifest + bundle.
- Операционный эффект: один сценарий запуска для CI/локальной подготовки модели, улучшенная воспроизводимость и проверяемость.
