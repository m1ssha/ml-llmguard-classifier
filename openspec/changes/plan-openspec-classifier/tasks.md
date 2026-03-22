## 1. Data Foundation and Labeling

- [x] 1.1 Создать структуру данных `classifier/data/{raw,processed}` и конфиг схемы разметки с обязательными полями
- [x] 1.2 Реализовать валидатор датасета для категорий покрытия (benign/malicious/borderline/obfuscated/near-miss)
- [x] 1.3 Добавить проверки языкового покрытия (ru/en/mixed/translit/distorted) и отчёт по распределениям
- [x] 1.4 Реализовать quality-check на shortcut-паттерны и блокировку обучения при нарушении критериев

## 2. Baseline and Encoder Training Pipelines

- [x] 2.1 Реализовать baseline pipeline (TF-IDF + Logistic Regression) с сохранением модели и метрик
- [x] 2.2 Реализовать encoder-based pipeline с сохранением весов, токенизатора и training metadata
- [x] 2.3 Унифицировать preprocessing между training и inference через общий модуль
- [x] 2.4 Добавить reproducibility controls (seed, config snapshot, versioned experiment outputs)

## 3. Hybrid Inference and API Contract

- [x] 3.1 Реализовать двухэтапный inference flow: binary stage и conditional threat stage
- [x] 3.2 Реализовать rule-based сигналы (prompt leakage/role override/bypass/obfuscation и др.)
- [x] 3.3 Объединить ML и rule-based результаты в единый объект `predict(text)`
- [x] 3.4 Зафиксировать и провалидировать JSON-контракт ответа (`is_malicious`, labels, confidences, `signals`)
- [x] 3.5 Добавить audit-логирование классов и confidence-значений для downstream policy/risk engine

## 4. Evaluation and Experiment Protocol

- [x] 4.1 Реализовать расчёт обязательных бинарных и мультиклассовых метрик
- [x] 4.2 Реализовать запуск эксперимента baseline-vs-encoder на одинаковом датасете
- [x] 4.3 Реализовать сравнение binary-only vs two-stage схемы
- [x] 4.4 Реализовать абляцию вклада rule-based сигналов и экспорт сводных таблиц

## 5. Integration Readiness and Definition of Done

- [x] 5.1 Подготовить CPU-only smoke/performance тесты инференса с порогами latency
- [x] 5.2 Добавить интеграционный слой для backend/gateway и контракты взаимодействия
- [x] 5.3 Подготовить итоговый отчёт: ограничения, риски, направления развития и соответствие DoD
