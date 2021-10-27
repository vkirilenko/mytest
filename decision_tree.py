#! usr/bin/python

from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from pathlib import Path

def decision_tree(args):

    with open(args.get("jsondata")) as data_path:
        data = json.load(data_path)  
 
    x_train = data['x_train']
    y_train = data['y_train']
    x_test = data['x_test']
    y_test = data['y_test']
    
    model = DecisionTreeClassifier(max_depth=4)
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    
    score = accuracy_score(y_test, y_pred)

    with open(args.get("accuracy"), 'w') as score_out:
        score_out.write(str(score))


if __name__ == '__main__':    

    var = {"jsondata": "~/models/Decision tree/input/data", 
    "accuracy": "~/models/Decision tree/output/accuracy"}

    Path(var.accuracy).parent.mkdir(parents=True, exist_ok=True)
    
decision_tree(var)