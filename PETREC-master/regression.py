import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split


# Split data into training and test sets. The default size of test data is 0.3.
# The argument independent_variables represents a list of independent variable names.
# The argument depdent_variable is the name of the dependent variable.
# return X_train, X_test, y_train, y_test
def split_train_test(df, independent_variables, dependent_variable, test_size=0.3):
    X_train, X_test, y_train, y_test = None, None, None, None
    # Your code here. Please following the code shown in German-credit.
    X_train, X_test, y_train, y_test = train_test_split(df[independent_variables], df[dependent_variable],
                                                        test_size=0.3, random_state=123)

    return X_train, X_test, y_train, y_test

#hello
# Fitting logistic regression model using training data and test data. X_train represents independent variable values in the training set
# X_test represent independent variable values in the test set; y_train represents the dependent variable values in the training set;
# y_test represent the dependent variable values in the test set.
def fit_logistic(X_train, X_test, y_train, y_test):
    pred_y = None
    from sklearn.linear_model import LogisticRegression
    '''
    Your code here... Please follow the German credit example
    First fit the model and obtain pred_y values
    '''
    algorithm = LogisticRegression()
    model = algorithm.fit(X_train, y_train)
    pred_y = model.predict(X_test)
    '''
    then
    1. print classification report
    '''
    from sklearn.metrics import classification_report
    for line in classification_report(y_test, pred_y).split("\n"):
        print line
    '''
    2. print accuracy. You can find how to get model accuracy by consulting the documentation of sklearn logistic regression. Hint: you need use score()
    Your code should print the measures as follows. The numbers you get could be be different because of random sampling
    '''
    print algorithm.score(X_test, y_test)
    '''

        precision    recall  f1-score   support

          0       0.80      0.89      0.85      3741
          1       0.74      0.59      0.65      1965

    avg / total       0.78      0.79      0.78      5706

    accuracy: 0.78671573782
    '''

    # don't worry if the measures you got are different. Random sampling may lead to different measures
    return pred_y  # predicted y values


# Fitting naive bayes using training data and test data
def fit_naive_bayes(X_train, X_test, y_train, y_test):
    pred_y = None
    from sklearn.naive_bayes import GaussianNB
    '''
    Your code here... Please follow the German credit example
    First fit the model and obtain pred_y values
    then
    '''
    algorithm = GaussianNB()
    model = algorithm.fit(X_train, y_train)
    pred_y = model.predict(X_test)
    '''
    1. print classification report
    '''
    from sklearn.metrics import classification_report
    for line in classification_report(y_test, pred_y).split("\n"):
        print line
    '''
    2. print accuracy. You can find how to get model accuracy by consulting the documentation of sklearn logistic regression. Hint: you need use score()
    Your code should print the measures as follows. The numbers you get could be be different because of random sampling
    '''
    print algorithm.score(X_test, y_test)
    '''
                 precision    recall  f1-score   support

              0       0.74      0.92      0.82      3741
              1       0.70      0.38      0.49      1965

    avg / total       0.72      0.73      0.70      5706

    accuracy: 0.730634419909'''


# fit logistic regression with cross-validation.
def fit_logistic_cv(X_train, X_test, y_train, y_test, cv=5):
    pred_y = None
    from sklearn.linear_model import LogisticRegressionCV
    '''
    Your code here... Please follow the German credit example.
    First fit the model and obtain pred_y values. You need to figure out how to do 5-fold cross validation.
    then
    '''
    algorithm = LogisticRegressionCV(cv)
    model = algorithm.fit(X_train, y_train)
    pred_y = model.predict(X_test)
    '''
    1. print classification report
    '''
    from sklearn.metrics import classification_report
    for line in classification_report(y_test, pred_y).split("\n"):
        print line
    '''
    2. print accuracy. You can find how to get model accuracy by consulting the documentation of sklearn logistic regression. Hint: you need use score()
    Your code should print the measures as follows. The numbers you get could be be different because of random sampling
    '''
    print algorithm.score(X_test, y_test)
    '''
                 precision    recall  f1-score   support

              0       0.80      0.90      0.85      3741
              1       0.75      0.59      0.66      1965

    avg / total       0.78      0.79      0.78      5706

    accuracy: 0.788643533123
    '''


def main():
    df = None
    df = pd.read_csv("magic04.csv")
    independent_variables = [col for col in df.columns if col != "class"]
    X_train, X_test, y_train, y_test = split_train_test(df, independent_variables, "class", test_size=0.3)
    print "Fit logististic regression:"
    fit_logistic(X_train, X_test, y_train, y_test)
    print "---------------------------"
    print "Fit naive bayes:"
    fit_naive_bayes(X_train, X_test, y_train, y_test)
    print "----------------------------"
    print "Fit logistic regression with 5-fold cross-validation:"
    fit_logistic_cv(X_train, X_test, y_train, y_test)
    ''' your output should look like the following. Again, the numbers you got may be different because of random sampling
    Fit logististic regression:
             precision    recall  f1-score   support

          0       0.80      0.89      0.85      3741
          1       0.74      0.59      0.65      1965

    avg / total       0.78      0.79      0.78      5706

    accuracy: 0.78671573782
    ---------------------------
    Fit naive bayes:
                 precision    recall  f1-score   support

              0       0.74      0.92      0.82      3741
              1       0.70      0.38      0.49      1965

    avg / total       0.72      0.73      0.70      5706

    accuracy: 0.730634419909
    ----------------------------
    Fit logistic regression with 5-fold cross-validation:
                 precision    recall  f1-score   support

              0       0.80      0.90      0.85      3741
              1       0.75      0.59      0.66      1965

    avg / total       0.78      0.79      0.78      5706

    accuracy: 0.788643533123
    '''


if __name__ == '__main__':
    main()






