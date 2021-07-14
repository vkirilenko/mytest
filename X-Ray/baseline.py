import json

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from soreva_metrics import calculate_metrics

def extract_basic_features(breast):
    predictors = {}
    # basic features
    for key in ["tissue_density_predicted", "cancer_probability_predicted"]:
        predictors[key] = breast[key]
    predictors["max_malignant"] = 0.0
    predictors["max_benign"] = 0.0
    # get max probability for the objects that contain malignant and benign in the class name
    for view in ["CC", "MLO"]:
        malignant_objs_probs = [obj["probability"] for obj in breast[view] if "malignant" in obj["object_type"]]
        benign_objs_probs = [obj["probability"] for obj in breast[view] if "benign" in obj["object_type"]]
        if malignant_objs_probs:
            predictors["max_malignant"] = max(malignant_objs_probs)
        if benign_objs_probs:
            predictors["max_benign"] = max(benign_objs_probs)
    
    return predictors

with open("data_train/data_train.json", "r") as fin:
    data_train = json.load(fin)

targets_train = pd.read_csv("data_train/targets_train.csv", index_col=0)

predictors = {}
for key, value in data_train.items():
    predictors[key] = extract_basic_features(value)

df_train = pd.DataFrame.from_dict(predictors, orient="index")
df_train = pd.merge(df_train, targets_train, left_index=True, right_index=True)
y_train = df_train["BiRads"].copy()
X_train = df_train.loc[:, "tissue_density_predicted":"max_benign"].copy()

splitter = StratifiedKFold(5, shuffle=True, random_state=24)

classifier = RandomForestClassifier(random_state=24)
predictions_cv = cross_val_predict(classifier, X_train, y_train, cv=splitter, n_jobs=-1)
print(calculate_metrics(y_train, predictions_cv))

classifier_gbm = GradientBoostingClassifier(random_state=24)
predictions_cv_gbm = cross_val_predict(classifier_gbm, X_train, y_train, cv=splitter, n_jobs=-1)
print(calculate_metrics(y_train, predictions_cv_gbm))
