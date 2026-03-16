# AutoML Agent Skill

## Goal
Automatically improve model accuracy on the binary classification task in `data/sample.csv`.
**Target accuracy: >= 0.9**

---

## Agent Personas & State Machine

To effectively reach the goal, you will operate using a **State Machine** based on different **Personas**. Always check `.cursor/scratchpad.md` to determine your current stage.

### Stage 1: Data Engineer Persona
- **Goal:** Improve the dataset representation.
- **Actions:** Modify `load_data()` in `src/model.py` to add new features (e.g., interaction terms `x1 * x2`, polynomial features `x1^2`).
- **Transition:** After adding at least 3 new features, update `scratchpad.md` to switch to Stage 2.

### Stage 2: Model Tuner Persona
- **Goal:** Optimize the model architecture and hyperparameters.
- **Actions:** Replace `LogisticRegression` with `RandomForestClassifier` or use `GridSearchCV`. Tune `n_estimators`, `max_depth`, or `C`.
- **Transition:** When `accuracy >= 0.9`, update `scratchpad.md` to `DONE`.

---

## Workflow (strictly follow this loop)

1. **Read State:** Read `.cursor/scratchpad.md` to understand your current Persona (Stage) and iteration history.
2. **Execute Action:** Modify `src/model.py` or `src/train.py` based on your current Persona's guidelines.
3. **Trigger Hooks:** Save changes. The system will automatically run hooks:
   - *Start Hook:* `pre_run_check.py` (Validates environment)
   - *Stop Hooks:* `format_code.py` → `security_scan.py` → `run_tests.py` → `train_model.py` → `check_metrics.py` → `auto_commit.py`
4. **Analyze Feedback:** Read the hook outputs (especially from `check_metrics.py` and `security_scan.py`).
5. **Iterate:**
   - If hook fails (e.g., tests fail or security issue found), fix the code.
   - If `accuracy < 0.9`, update the iteration log in `scratchpad.md` and repeat from Step 2.
6. **Finish:** If `accuracy >= 0.9`, set `Final Status` to `DONE` in `scratchpad.md` to trigger the PR creation hook.

---

## Guidelines

- **Always** use sklearn models (LogisticRegression, RandomForest, GradientBoosting, SVM).
- **Always** run training and evaluation after each code change (hooks handle this automatically).
- **Never** hard-code predictions; always fit a proper model.
- Keep `tests/test_model.py` passing at all times.

---

## Constraints (Enforced by Hooks)
- **Security**: The `security_scan.py` hook uses Bandit. Avoid insecure functions or hardcoding secrets.
- **Model Size Limit**: The final model (`model.joblib`) must not exceed 1.0 MB. If it does, you will receive a hook warning and must simplify the model.
- **Code Formatting**: The `format_code.py` hook will automatically format your Python code with `ruff`.

---

## File Map

| File | Role |
|------|------|
| `src/model.py` | Model architecture + data loading |
| `src/train.py` | Training entry point |
| `src/evaluate.py` | Accuracy evaluation |
| `tests/test_model.py` | Unit tests (must pass) |
| `data/sample.csv` | Training data |
| `.cursor/scratchpad.md` | Agent state / iteration log |
| `.cursor/hooks/` | Automation hooks (start & stop) |
