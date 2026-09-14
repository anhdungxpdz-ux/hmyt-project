# -*- coding: utf-8 -*-
"""
Lab Suy tim cap toc (3.4 suy_tim_risk_dxai) - ban giai (instructor reference solution).
Chay toan bo 5 buoi: EDA -> Baseline -> SMOTE+ExtraTrees -> SHAP -> tong hop so lieu bao cao.
"""
import json
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.metrics import (
    accuracy_score, matthews_corrcoef, f1_score, precision_score,
    recall_score, roc_auc_score, confusion_matrix
)
from imblearn.over_sampling import SMOTE
import shap

RANDOM_STATE = 42
OUT = {}

# ---------------------------------------------------------------------------
# Buoi 1: EDA + Preprocessing
# ---------------------------------------------------------------------------
df = pd.read_csv("heart_failure_clinical_records.csv")
OUT["n_rows"] = len(df)
OUT["n_cols"] = df.shape[1]
OUT["missing_total"] = int(df.isna().sum().sum())
OUT["death_event_counts"] = df["death_event"].value_counts().to_dict()
OUT["death_event_pct"] = (df["death_event"].value_counts(normalize=True) * 100).round(2).to_dict()

features = [c for c in df.columns if c not in ("death_event",)]
X = df[features]
y = df["death_event"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)
OUT["train_size"] = len(X_train)
OUT["test_size"] = len(X_test)
OUT["train_death_pct"] = round(y_train.mean() * 100, 2)
OUT["test_death_pct"] = round(y_test.mean() * 100, 2)

# Correlation voi bien muc tieu (tren TOAN BO du lieu goc, chi de EDA/report,
# khong dung de chon dac trung train model - tranh leakage quyet dinh)
corr_with_target = df.corr(numeric_only=True)["death_event"].drop("death_event").sort_values(key=abs, ascending=False)
OUT["top_correlations"] = corr_with_target.round(3).to_dict()

# Chuan hoa: fit CHI tren Train
scaler = StandardScaler()
X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=features, index=X_train.index)
X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=features, index=X_test.index)

# ---------------------------------------------------------------------------
# Buoi 2: Baseline (Logistic Regression + Random Forest) - tai lap chicco2020machine
# ---------------------------------------------------------------------------
def evaluate(model, X_te, y_te, name):
    pred = model.predict(X_te)
    proba = model.predict_proba(X_te)[:, 1] if hasattr(model, "predict_proba") else None
    metrics = {
        "accuracy": round(accuracy_score(y_te, pred) * 100, 1),
        "mcc": round(matthews_corrcoef(y_te, pred), 3),
        "f1": round(f1_score(y_te, pred) * 100, 1),
        "precision": round(precision_score(y_te, pred) * 100, 1),
        "recall": round(recall_score(y_te, pred) * 100, 1),
    }
    if proba is not None:
        metrics["auc"] = round(roc_auc_score(y_te, proba) * 100, 1)
    cm = confusion_matrix(y_te, pred).tolist()
    metrics["confusion_matrix"] = cm
    print(f"[{name}]", metrics)
    return metrics

lr = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
lr.fit(X_train_scaled, y_train)
OUT["logreg_baseline"] = evaluate(lr, X_test_scaled, y_test, "LogisticRegression")

rf = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)
rf.fit(X_train_scaled, y_train)
OUT["rf_baseline"] = evaluate(rf, X_test_scaled, y_test, "RandomForest-baseline")

# ---------------------------------------------------------------------------
# Buoi 3: SMOTE (CHI tren Train) + Extra Trees - huong toi ishaq2021improving
# ---------------------------------------------------------------------------
smote = SMOTE(random_state=RANDOM_STATE)
X_train_sm, y_train_sm = smote.fit_resample(X_train_scaled, y_train)
OUT["smote_train_size"] = len(X_train_sm)
OUT["smote_train_death_pct"] = round(y_train_sm.mean() * 100, 2)

et = ExtraTreesClassifier(n_estimators=300, random_state=RANDOM_STATE)
et.fit(X_train_sm, y_train_sm)
OUT["extratrees_smote"] = evaluate(et, X_test_scaled, y_test, "ExtraTrees+SMOTE")

# Random Forest + SMOTE de doi chieu (khong SMOTE la baseline o tren)
rf_sm = RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE)
rf_sm.fit(X_train_sm, y_train_sm)
OUT["rf_smote"] = evaluate(rf_sm, X_test_scaled, y_test, "RandomForest+SMOTE")

# ---------------------------------------------------------------------------
# Buoi 4: XAI voi SHAP tren mo hinh tot nhat (ExtraTrees+SMOTE)
# ---------------------------------------------------------------------------
best_model_name = max(
    [("ExtraTrees+SMOTE", OUT["extratrees_smote"]), ("RandomForest+SMOTE", OUT["rf_smote"]),
     ("RandomForest-baseline", OUT["rf_baseline"])],
    key=lambda kv: kv[1]["mcc"]
)[0]
OUT["best_model_by_mcc"] = best_model_name

explainer = shap.TreeExplainer(et)
shap_values = explainer.shap_values(X_test_scaled)
# shap tra ve list cho binary classifier cu hoac array 3D cho ban moi - chuan hoa ve lop 1 (tu vong)
if isinstance(shap_values, list):
    sv_class1 = shap_values[1]
elif shap_values.ndim == 3:
    sv_class1 = shap_values[:, :, 1]
else:
    sv_class1 = shap_values

mean_abs_shap = np.abs(sv_class1).mean(axis=0)
shap_importance = pd.Series(mean_abs_shap, index=features).sort_values(ascending=False)
OUT["shap_feature_importance"] = shap_importance.round(4).to_dict()
OUT["shap_top2"] = list(shap_importance.index[:2])

plt.figure()
shap.summary_plot(sv_class1, X_test_scaled, show=False, plot_type="bar")
plt.tight_layout()
plt.savefig("shap_summary_bar.png", dpi=150)
plt.close()

plt.figure()
shap.summary_plot(sv_class1, X_test_scaled, show=False)
plt.tight_layout()
plt.savefig("shap_summary_beeswarm.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# Xuat toan bo so lieu ra JSON de dung khi viet bao cao
# ---------------------------------------------------------------------------
with open("results.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)

print("\n=== HOAN TAT - xem results.json + shap_summary_*.png ===")
