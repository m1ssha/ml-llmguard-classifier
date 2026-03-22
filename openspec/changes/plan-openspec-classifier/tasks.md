## 1. Data Foundation and Labeling

- [ ] 1.1 Создать структуру данных `classifier/data/{raw,processed}` и конфиг схемы разметки с обязательными полями
- [ ] 1.2 Реализовать валидатор датасета для категорий покрытия (benign/malicious/borderline/obfuscated/near-miss)
- [ ] 1.3 Добавить проверки языкового покрытия (ru/en/mixed/translit/distorted) и отчёт по распределениям
- [ ] 1.4 Реализовать quality-check на shortcut-паттерны и блокировку обучения при нарушении критериев

## 2. Baseline and Encoder Training Pipelines

- [ ] 2.1 Реализовать baseline pipeline (TF-IDF + Logistic Regression) с сохранением модели и метрик
- [ ] 2.2 Реализовать encoder-based pipeline с сохранением весов, токенизатора и training metadata
- [ ] 2.3 Унифицировать preprocessing между training и inference через общий модуль
- [ ] 2.4 Добавить reproducibility controls (seed, config snapshot, versioned experiment outputs)

## 3. Hybrid Inference and API Contract

- [ ] 3.1 Реализовать двухэтапный inference flow: binary stage и conditional threat stage
- [ ] 3.2 Реализовать rule-based сигналы (prompt leakage/role override/bypass/obfuscation и др.)
- [ ] 3.3 Объединить ML и rule-based результаты в единый объект `predict(text)`
- [ ] 3.4 Зафиксировать и провалидировать JSON-контракт ответа (`is_malicious`, labels, confidences, `signals`)
- [ ] 3.5 Добавить audit-логирование классов и confidence-значений для downstream policy/risk engine

## 4. Evaluation and Experiment Protocol

- [ ] 4.1 Реализовать расчёт обязательных бинарных и мультиклассовых метрик
- [ ] 4.2 Реализовать запуск эксперимента baseline-vs-encoder на одинаковом датасете
- [ ] 4.3 Реализовать сравнение binary-only vs two-stage схемы
- [ ] 4.4 Реализовать абляцию вклада rule-based сигналов и экспорт сводных таблиц

## 5. Integration Readiness and Definition of Done

- [ ] 5.1 Подготовить CPU-only smoke/performance тесты инференса с порогами latency
- [ ] 5.2 Добавить интеграционный слой для backend/gateway и контракты взаимодействия
- [ ] 5.3 Подготовить итоговый отчёт: ограничения, риски, направления развития и соответствие DoD
