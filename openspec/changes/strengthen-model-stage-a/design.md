## Context

Проект уже имеет оформленный MVP-каркас классификатора атак на LLM: dataset validation, baseline и surrogate encoder training, two-stage inference, rule signals, evaluation и gateway contract. Однако для задачи выявления адаптивных атак текущая реализация остаётся недостаточно сильной по существу: мало подтверждённого adversarial coverage в данных, rule-based слой слишком прост, encoder-путь пока не даёт полноценной семантической устойчивости, а evaluation ограничен в основном классическими offline-метриками.

Изменение затрагивает несколько модулей сразу: [`classifier/src/dataset/`](classifier/src/dataset/), [`classifier/src/training/`](classifier/src/training/), [`classifier/src/inference/`](classifier/src/inference/), [`classifier/src/evaluation/`](classifier/src/evaluation/), [`classifier/src/api/`](classifier/src/api/). Стейкхолдеры: ML-разработчик, security researcher, backend/gateway integrator.

Ограничения:
- inference должен оставаться пригодным для CPU-first deployment;
- gateway contract должен сохранять обратную совместимость или иметь явное versioning-расширение;
- улучшения должны быть измеримы через воспроизводимые эксперименты, а не только декларативно описаны.

## Goals / Non-Goals

**Goals:**
- Усилить датасетное покрытие под adaptive attacks: multilingual, translit, obfuscation, near-miss benign, staged prompts, adversarial holdouts.
- Перевести hybrid detector от простых keyword-флагов к более богатому explainable rule-scoring слою.
- Добавить более содержательно сильный encoder-based путь, сохранив CPU-совместимость inference.
- Зафиксировать security-oriented evaluation protocol: robustness, calibration, threshold tuning и false-positive analysis.
- Подготовить inference/result contract к боевому использованию через evidence, versioning и threshold metadata.

**Non-Goals:**
- Session-aware multi-turn защита.
- Полноценная интеграция с RAG/tool-calling policy engine.
- Переход на GPU-only serving.
- Создание финального production orchestration, CI/CD и инфраструктуры rollout beyond artifact-level requirements.

## Decisions

1. **Расширять проект через отдельный Stage A change, а не переписывать исходный MVP change**
   - Решение: оформить улучшения отдельным OpenSpec change.
   - Почему: сохраняется история исходного MVP и появляется контролируемый roadmap усиления модели.
   - Альтернатива: дорабатывать существующий change; отвергнуто, потому что теряется граница между baseline-MVP и hardening-этапом.

2. **Выделить датасетное усиление в самостоятельную capability**
   - Решение: формализовать требования к adversarial coverage, holdout splits и quality policy в отдельной capability.
   - Почему: именно данные являются главным ограничителем качества adaptive-attack detection; их нужно фиксировать как требования, а не как неявные implementation details.
   - Альтернатива: ограничиться задачами в `tasks.md`; отвергнуто, потому что без capability-спека требования будут расплывчаты.

3. **Сделать hybrid detector объяснимым и многоуровневым**
   - Решение: развить rules в scoring/evidence layer с нормализацией текста, поддержкой obfuscation-паттернов и выдачей explainable evidence.
   - Почему: adaptive attacks часто обходят literal keyword matching, а downstream security workflows нуждаются в интерпретируемом решении.
   - Альтернатива: опираться только на ML confidence; отвергнуто из-за слабой explainability и меньшей устойчивости на edge-cases.

4. **Добавить stronger encoder как второй production-candidate поверх текущего surrogate**
   - Решение: не удалять текущий char/subword surrogate сразу, а сравнивать его с новым encoder-based кандидатом на одинаковом датасете и robustness-benchmark.
   - Почему: это сохраняет baseline для научного сравнения и снижает риск регресса latency/операционной сложности.
   - Альтернатива: полная одномоментная замена текущего encoder pipeline; отвергнуто из-за высокой неопределённости по качеству и эксплуатационным параметрам.

5. **Расширить evaluation от обычных offline metrics к adversarial protocol**
   - Решение: добавить обязательные stress-test срезы по obfuscation, paraphrase, language transfer, benign security discussions и policy bypass.
   - Почему: классические accuracy/F1 недостаточны для security-задачи с адаптивным противником.
   - Альтернатива: оставить только existing experiment suite; отвергнуто как недостаточное для доказательства содержательной силы модели.

6. **Считать inference artifact bundle частью design boundary**
   - Решение: фиксировать не только веса модели, но и thresholds, label maps, calibration metadata, versioning и evidence schema как обязательные боевые артефакты.
   - Почему: production-ready classifier определяется воспроизводимым inference bundle, а не только сериализованным estimator.
   - Альтернатива: хранить только `joblib`-модели; отвергнуто, потому что этого недостаточно для rollout, rollback и стабильной интеграции.

## Risks / Trade-offs

- **[Risk]** Расширение датасета увеличит стоимость разметки и time-to-iteration → **Mitigation**: приоритизировать adversarial holdouts и наиболее рискованные threat families в первой волне.
- **[Risk]** Более сильный encoder может ухудшить CPU latency → **Mitigation**: оставлять surrogate как baseline, сравнивать latency/quality и предусмотреть ONNX/квантование на следующем этапе.
- **[Risk]** Более сложный rule-engine может поднять false positives на benign security discussions → **Mitigation**: добавить отдельные near-miss benign тестовые срезы и evidence-driven threshold tuning.
- **[Risk]** Расширение inference-контракта может затронуть backend consumers → **Mitigation**: вводить schema versioning и additive-compatible поля.
- **[Trade-off]** Более строгий adversarial evaluation замедлит цикл экспериментов, но даст более честную картину robustness.
- **[Trade-off]** Поддержка двух encoder paths увеличит сложность сопровождения, но облегчит сравнение и постепенный rollout.

## Migration Plan

1. Добавить новые и изменённые capability-specs для Stage A.
2. Реализовать датасетные требования и adversarial split policy.
3. Реализовать усиленный rule/evidence layer и расширенный inference bundle.
4. Добавить stronger encoder candidate и сравнение с surrogate.
5. Провести adversarial evaluation, calibration и threshold tuning.
6. Обновить gateway-facing contract и итоговые отчёты.
7. Выполнить rollout в режиме offline/shadow evaluation перед боевым включением.

Rollback strategy:
- сохранять текущий surrogate pipeline и исходный inference contract как fallback;
- versioning артефактов должен позволять быстро вернуться к предыдущему комплекту модели и thresholds.

## Open Questions

- Какой именно encoder станет основным production-candidate: компактный transformer, multilingual encoder или другой CPU-friendly вариант?
- Нужен ли обязательный ONNX-export уже в этом change или это должен быть следующий deployment-focused этап?
- Какие threat families приоритизировать в первой волне adversarial data expansion, если ресурсы на разметку ограничены?
- Какой режим принятия решения нужен по умолчанию для gateway: balanced, high recall security mode или low false positive mode?
