## 1. CLI entrypoint and orchestration scaffold

- [ ] 1.1 Создать `classifier/scripts/run_prompt_injection_train_export.py` с CLI-парсером аргументов `dataset_id`, `output_root`, `seed`, `experiment_name`, `include_baseline`, `profile` и валидацией допустимых значений профиля.
- [ ] 1.2 Реализовать orchestration flow одного запуска (load → normalize → train encoder → evaluate → export bundle) как thin-wrapper над существующими модулями `classifier/src/*`.

## 2. Dataset normalization and fail-fast validation

- [ ] 2.1 Добавить alias-логику сопоставления колонок/лейблов HF-датасета `neuralchemy/Prompt-injection-dataset` с использованием существующих dataset-модулей проекта.
- [ ] 2.2 Реализовать понятные ошибки при отсутствии обязательных семантических полей (со списком ожидаемых алиасов и фактически найденных колонок).
- [ ] 2.3 Обеспечить преобразование данных в формат project samples, совместимый с текущими training pipelines.

## 3. Training, profiling, and artifact export contract

- [ ] 3.1 Интегрировать запуск stronger encoder pipeline с контролем воспроизводимости через `seed`.
- [ ] 3.2 Реализовать опциональный baseline-проход при `include_baseline=true` и включение baseline-метрик в отчёт без нарушения основного encoder export.
- [ ] 3.3 Экспортировать обязательный bundle-файлов: `encoder_model.joblib`, `tokenizer.joblib`, `label_mapping.json`, `thresholds.json`, `training_metadata.json`, `artifact_manifest.json`, `evaluation_report.json`.
- [ ] 3.4 В `evaluation_report.json` сохранять binary метрики для `balanced` и `high_recall_security`, robustness slices и ссылки/пути к экспортированным артефактам.

## 4. Contract validation tests

- [ ] 4.1 Добавить smoke-тест для нового скрипта в `classifier/tests/` (проверка запуска и создания output директории эксперимента).
- [ ] 4.2 Добавить тест структуры bundle, проверяющий наличие всех обязательных артефактов и ключевых секций `evaluation_report.json`/`artifact_manifest.json`.
- [ ] 4.3 Обновить/добавить фикстуры или моки датасета для детерминированного тестового прогона без дублирования production-логики.

## 5. Documentation and readiness checks

- [ ] 5.1 Добавить в `README.md` короткую инструкцию запуска скрипта с примером команды и описанием ключевых параметров.
- [ ] 5.2 Проверить, что generated bundle загружается inference-слоем без обращения к training internals (через существующий inference-контракт/тест).
- [ ] 5.3 Прогнать тесты и зафиксировать, что change готов к apply/implementation по критериям приёмки.
