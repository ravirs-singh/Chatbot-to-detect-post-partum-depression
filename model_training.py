import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.svm import SVC
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LogisticRegression 
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report
from xgboost import XGBClassifier
import pickle

data = pd.read_csv("C:/Users/Lenovo/Desktop/HIM/datasetFinal.csv")
#data.info()
#print(data.head())
#data["Response"].value_counts()

#print(data[data["Response"]  ==  "YES (CHECKED)"]["Question"][53])
money_from_family_friends  =  data[data["Response"]  ==  "YES (CHECKED)"]["Question"][53]
paycheck_from_job  =  data[data["Response"]  ==  "YES (CHECKED)"]["Question"][579]
money_from_buisness = "Source of household income - money from a business, fees, dividends or rental income"

data.loc[(data["Response"] == "YES (CHECKED)") & (data["Question"] == money_from_family_friends), "Response",] = data.loc[
(data["Response"] == "YES (CHECKED)") & (data["Question"] == money_from_family_friends), "Response",].apply(
lambda x: "YES"
)


data.loc[
(data["Response"] == "YES (CHECKED)") & (data["Question"] == money_from_buisness), "Response",
] = data.loc[
(data["Response"] == "YES (CHECKED)") & (data["Question"] == money_from_buisness), "Response",
].apply(
lambda x: "NO"
)

data.loc[
(data["Response"] == "YES (CHECKED)") & (data["Question"] == paycheck_from_job), "Response",
] = data.loc[
(data["Response"] == "YES (CHECKED)") & (data["Question"] == paycheck_from_job), "Response",
].apply(
lambda x: "NO"
)

no_list = [
"None (0 cig)", "NONSMOKER",
"NBW (>2500g)", "NONDRINKER",
"NORMAL (18.5-24.9)",
"1 or more",
"DRINKER WHO QUIT",
"OK  (NOT  LBW  OR  PRETERM)",
"Intended",
"SMOKER WHO QUIT",
"1-5/day",
"#CIGS  REDUCED",
"< 1/day",
"NONSMOKR  RESUMED", "#DRKS  REDUCED",
"OBSE",
"NO",
]

# data["Response"] = data["Response"].apply(lambda x: "NO" if x in no_list else x)

data["Response"]  =  data["Response"].apply(lambda  x:  "NO"  if  x  in  no_list  else  "YES")

#print(data["Response"].value_counts())
#print(data.head())

#exclude unnecessary columns
data.drop(
columns=[
"Year",
"Data_Value_Type", "BreakOutId",
"LocationAbbr", "LocationDesc", "Sample_Size", "Break_Out",
],
inplace=True, axis=1,
)

#print(data.head())

Question = data["Question"]
data.drop("Question",  axis=1,  inplace=True)

#print(data.head())

le = OneHotEncoder()
le.fit(data[["Class", "Topic", "Response", "Break_Out_Category"]])
categorized_data = le.transform(
data[["Class", "Topic", "Response", "Break_Out_Category"]]
).toarray()

#print(categorized_data)
le.get_feature_names(["Class", "Topic", "Response", "BOC"])

new_data  =  pd.DataFrame( categorized_data,
columns=le.get_feature_names(["Class",  "Topic",  "Response",  "BOC"]),
)

new_data  =  pd.concat([new_data, data[["Data_Value", "Low_Confidence_Limit", "High_Confidence_Limit"]]], axis=1,)

#print(len(new_data["Low_Confidence_Limit"]), len(new_data["High_Confidence_Limit"]))
new_data = new_data.dropna()

# print(new_data.columns)

y  =  new_data[["Response_NO",  "Response_YES"]]
X  =  new_data.drop(columns=["Response_NO",  "Response_YES"])

sc = StandardScaler()
X  =  sc.fit_transform(X)

y  =  y.drop(["Response_NO"],  axis=1)
y  =  np.array(y)

#divide data as train and test sets
X_train,  X_test,  y_train,  y_test  =  train_test_split(X,  y,  test_size=0.2,  random_state=0)
print(f"Train Size {len(X_train)}")
print(f"Test Size {len(X_test)}")


# save the model to disk
#filename = 'finalized_model.pkl'


# Logistic Regression
LR = LogisticRegression()
LR.fit(X_train,  y_train.ravel())
pickle.dump(LR, open("finalized_model_LR.pkl", 'wb'))
test_predict  =  LR.predict(X_test)
train_predict  =  LR.predict(X_train)
print(classification_report(y_test, test_predict))
print(classification_report(y_train, train_predict))
print("R2 ",r2_score(y_test,test_predict ) )
print("Mean square error",mean_squared_error(y_test,test_predict ) )

#KNN classifier
# KNNModel = KNeighborsClassifier(n_neighbors=10)
# KNNModel.fit(X_train,  y_train.ravel())
# #pickle.dump(KNNModel, open("finalized_model_KNN.pkl", 'wb'))
# test_predict  =  KNNModel.predict(X_test)
# train_predict  =  KNNModel.predict(X_train)
# print("R2 ",r2_score(y_test,test_predict ) )
# print("Mean square error",mean_squared_error(y_test,test_predict ) )




# print("Report KNN",mean_squared_error(y_test,test_predict ) )
#print("Report",r2_score(test_predict,train_predict ) )

#Decision Tree(Gini)
# dtg = DecisionTreeClassifier()
# dtg = dtg.fit(X_train,y_train.ravel())
# pickle.dump(dtg, open("finalized_model_XGB.pkl", 'wb'))
# test_predict = dtg.predict(X_test)
# train_predict = dtg.predict(X_train)
# print(classification_report(y_test, test_predict))
# print(classification_report(y_train, train_predict))
# print("R2 ",r2_score(y_test,test_predict ) )
# print("Mean square error",mean_squared_error(y_test,test_predict ) )

#Decision Tree(Entropy)
# dte = DecisionTreeClassifier(criterion="entropy", max_depth=3)
# dte = dte.fit(X_train,y_train)
# pickle.dump(dte, open("finalized_model_XGB.pkl", 'wb'))
# test_predict = dte.predict(X_test)
# train_predict = dte.predict(X_train)
# print("R2 ",r2_score(y_test,test_predict ) )
# print("Mean square error",mean_squared_error(y_test,test_predict ) )

# print(classification_report(y_test, test_predict))
# print(classification_report(y_train, train_predict))


#Random Forest
# rfc=RandomForestClassifier(n_estimators=100)
# rfc.fit(X_train,y_train.ravel())
# pickle.dump(rfc, open("finalized_model_XGB.pkl", 'wb'))
# test_predict = rfc.predict(X_test)
# train_predict = rfc.predict(X_train)
# print(classification_report(y_test, test_predict))
# print(classification_report(y_train, train_predict))
# print("R2 ",r2_score(y_test,test_predict ) )
# print("Mean square error",mean_squared_error(y_test,test_predict ) )

# # Support vestor machine
# clf = svm.SVC(kernel='linear')
# clf.fit(X_train, y_train.ravel())
# pickle.dump(clf, open("finalized_model_XGB.pkl", 'wb'))
# test_predict = clf.predict(X_test)
# train_predict = clf.predict(X_train)

# # # print("R2 ",r2_score(y_test,test_predict ) )
# # # print("Mean square error",mean_squared_error(y_test,test_predict ) )
# print(classification_report(y_test, test_predict))
# print(classification_report(y_train, train_predict))


# Naive Bayes
# model = GaussianNB()
# model.fit(X_train, y_train.ravel())
# pickle.dump(model, open("finalized_model_XGB.pkl", 'wb'))
# test_predict = model.predict(X_test)
# train_predict = model.predict(X_train)
# print("R2 ",r2_score(y_test,test_predict ) )
# print("Mean square error",mean_squared_error(y_test,test_predict ) )

# print(classification_report(y_test, test_predict))
# print(classification_report(y_train, train_predict))


# AdaBoost
# svc=SVC(probability=True, kernel='linear')
# adaboost=AdaBoostClassifier(n_estimators=50, base_estimator=svc,learning_rate=1)
# model = adaboost.fit(X_train, y_train)
# # pickle.dump(model, open("finalized_model_XGB.pkl", 'wb'))
# test_predict = model.predict(X_test)
# train_predict = model.predict(X_train)
# # print("R2 ",r2_score(y_test,test_predict ) )
# # print("Mean square error",mean_squared_error(y_test,test_predict ) )

# print(classification_report(y_test, test_predict))
# print(classification_report(y_train, train_predict))

#XGBOOST
# xgboost = XGBClassifier(use_label_encoder=False)
# xgboost.fit(X_train, y_train.ravel())
# pickle.dump(xgboost, open("finalized_model_XGB.pkl", 'wb'))
# test_predict = xgboost.predict(X_test)
# train_predict = xgboost.predict(X_train)

# print("R2 ",r2_score(y_test,test_predict ) )
# print("Mean square error",mean_squared_error(y_test,test_predict ) )

# print(classification_report(y_test, test_predict))
# print(classification_report(y_train, train_predict))

