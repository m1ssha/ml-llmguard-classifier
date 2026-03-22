## Why

Текущий MVP-классификатор хорошо оформлен архитектурно, но содержательная сила детекции ограничена: в репозитории не хватает adversarial-grade датасетного покрытия, rule-layer остаётся слишком поверхностным, а encoder-пайплайн пока реализован как лёгкий surrogate. Это изменение нужно сейчас, чтобы перевести проект от формально завершённого MVP к более убедительной и измеримо устойчивой модели для выявления адаптивных атак на LLM.

## What Changes

- Добавить capability для усиления датасета и evaluation-протокола под adaptive attacks: multilingual, translit, obfuscation, near-miss benign, staged attacks и adversarial holdout splits.
- Добавить capability для усиления hybrid detection: расширенный rule engine, richer evidence/signals, calibration и threshold management.
- Добавить capability для перехода от surrogate encoder к содержательно более сильному encoder-based pipeline при сохранении CPU-first и gateway-ready ограничений.
- Зафиксировать требования к red-team oriented экспериментам: robustness against paraphrase, obfuscation, policy-bypass и false positives на benign security discussions.

## Capabilities

### New Capabilities
- `adaptive-dataset-hardening`: требования к расширенному датасетному покрытию, quality checks и adversarial holdout-наборам для адаптивных атак.
- `hybrid-detector-hardening`: требования к усиленному rule-based слою, evidence/signals, калибровке confidence и threshold management.
- `robust-encoder-upgrade`: требования к более сильному encoder-based пайплайну и его сравнению с текущим surrogate baseline.
- `adversarial-evaluation-protocol`: требования к robustness-экспериментам и security-oriented метрикам сверх базовой offline-оценки.

### Modified Capabilities
- `classifier-dataset-and-labeling`: расширить требования к покрытию данных за пределы базовых категорий, добавив adversarial splits и обязательное покрытие сложных benign/obfuscated сценариев.
- `classifier-training-and-evaluation`: расширить требования к экспериментам, чтобы они включали calibration, robustness-срезы и сравнение surrogate vs stronger encoder.
- `classifier-inference-interface`: расширить контракт inference-результата за счёт evidence, versioning и threshold metadata для боевого использования.
- `llm-attack-classifier-mvp`: уточнить Definition of Done, чтобы MVP считался готовым только при наличии усиленного adversarial coverage и security-oriented evaluation.

## Impact

- Затронуты модули `classifier/src/dataset/`, `classifier/src/training/`, `classifier/src/inference/`, `classifier/src/evaluation/`, `classifier/src/api/`.
- Появятся новые/обновлённые OpenSpec-спеки в `openspec/changes/strengthen-model-stage-a/specs/`.
- Потребуется обновление конфигов, тестов, артефактов экспериментов и итогового inference-контракта для gateway/backend.
- Возможны новые зависимости для encoder export/calibration и дополнительные вычислительные требования на этапе обучения, при сохранении CPU-совместимого inference.
