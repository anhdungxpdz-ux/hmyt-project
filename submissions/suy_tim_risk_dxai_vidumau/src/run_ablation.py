# -*- coding: utf-8 -*-
"""Ablation: anh huong cua bien 'time' (nghi van leakage) + thu nhieu cau hinh
de xem co the tiem can 92.6% (ishaq2021improving) hay khong."""
import json
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, matthews_corrcoef, f1_score
from imblearn.over_sampling import SMOTE

RANDOM_STATE = 42
df = pd.read_csv("heart_failure_clinical_records.csv")
features_full = [c for c in df.columns if c != "death_event"]
features_no_time = [c for c in features_full if c != "time"]
features_2 = ["serum_creatinine", "ejection_fraction"]

X = df[features_full]
y = df["death_event"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)

results = []

def run_config(feat_list, feat_name, use_smote, model_name, model):
    Xtr = X_train[feat_list]
    Xte = X_test[feat_list]
    scaler = StandardScaler()
    Xtr_s = scaler.fit_transform(Xtr)
    Xte_s = scaler.transform(Xte)
    if use_smote:
        Xtr_s, ytr = SMOTE(random_state=RANDOM_STATE).fit_resample(Xtr_s, y_train)
    else:
        ytr = y_train
    model.fit(Xtr_s, ytr)
    pred = model.predict(Xte_s)
    acc = round(accuracy_score(y_test, pred) * 100, 1)
    mcc = round(matthews_corrcoef(y_test, pred), 3)
    f1 = round(f1_score(y_test, pred) * 100, 1)
    # 5-fold CV tren train (sau smote neu co) de xem on dinh hon 1 split khong
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(model, Xtr_s, ytr, cv=cv, scoring="accuracy")
    row = {
        "features": feat_name, "smote": use_smote, "model": model_name,
        "test_accuracy": acc, "test_mcc": mcc, "test_f1": f1,
        "cv_accuracy_mean": round(cv_scores.mean() * 100, 1),
        "cv_accuracy_std": round(cv_scores.std() * 100, 1),
    }
    results.append(row)
    print(row)

configs = [
    (features_full, "full(12)", False, "RF", RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)),
    (features_no_time, "full-time(11)", False, "RF", RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)),
    (features_2, "creatinine+EF(2)", False, "RF", RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)),
    (features_full, "full(12)", True, "ExtraTrees", ExtraTreesClassifier(n_estimators=300, random_state=RANDOM_STATE)),
    (features_no_time, "full-time(11)", True, "ExtraTrees", ExtraTreesClassifier(n_estimators=300, random_state=RANDOM_STATE)),
    (features_full, "full(12)", True, "GradientBoosting", GradientBoostingClassifier(random_state=RANDOM_STATE)),
    (features_full, "full(12)", True, "RF-500", RandomForestClassifier(n_estimators=500, max_depth=8, random_state=RANDOM_STATE)),
    (features_2, "creatinine+EF(2)", True, "ExtraTrees", ExtraTreesClassifier(n_estimators=300, random_state=RANDOM_STATE)),
]

for feat, fname, sm, mname, model in configs:
    run_config(feat, fname, sm, mname, model)

with open("ablation_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

best = max(results, key=lambda r: r["test_mcc"])
print("\n=== BEST BY MCC ===")
print(best)
