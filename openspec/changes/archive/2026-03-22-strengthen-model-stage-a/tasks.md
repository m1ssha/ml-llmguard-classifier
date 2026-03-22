## 1. Dataset Hardening

- [x] 1.1 Спроектировать расширенную схему покрытия для adaptive-attack датасета: multilingual, translit, obfuscation, staged prompts и benign near-miss категории
- [x] 1.2 Добавить подготовку и валидацию adversarial holdout splits для obfuscation, policy-bypass, multilingual transfer и benign security discussions
- [x] 1.3 Усилить quality checks датасета проверками на присутствие benign near-miss и adversarially rewritten malicious samples

## 2. Hybrid Detector Hardening

- [x] 2.1 Расширить rule engine нормализацией obfuscation-паттернов, spaced tokens, Unicode confusables и transliteration variants
- [x] 2.2 Добавить structured evidence/signals в inference result без нарушения обратной совместимости контракта
- [x] 2.3 Реализовать загрузку deployment profile, thresholds и calibration metadata в inference service

## 3. Stronger Encoder Upgrade

- [x] 3.1 Добавить более сильный encoder-based training path как production-candidate наряду с текущим surrogate pipeline
- [x] 3.2 Реализовать экспорт полного inference artifact bundle: model/tokenizer or estimator, label mapping, thresholds, metadata и version manifest
- [x] 3.3 Добавить сравнение surrogate и stronger encoder по качеству и CPU latency на одинаковом наборе срезов

## 4. Adversarial Evaluation Protocol

- [x] 4.1 Расширить evaluation runner robustness-сценариями: paraphrase, obfuscation, language transfer, policy bypass и benign security discussions
- [x] 4.2 Добавить отчёт по false positives на benign security prompts и threshold-specific operating points
- [x] 4.3 Экспортировать deployment profiles для balanced и high-recall security режимов

## 5. Integration and Readiness

- [x] 5.1 Обновить inference/output contract versioning и audit logging для evidence и deployment-profile metadata
- [x] 5.2 Обновить тесты, smoke checks и отчёты так, чтобы они валидировали Stage A readiness criteria
- [x] 5.3 Подготовить итоговый отчёт по усилению модели с сравнением до/после и рекомендацией по rollout/shadow evaluation
