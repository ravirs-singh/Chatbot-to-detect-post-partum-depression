#pip install flask
from flask import Flask, render_template, request, redirect, url_for
from chatterbot import ChatBot
import sqlite3
import time
import pandas as pd
import sys
from sklearn.preprocessing import StandardScaler
import numpy as np
import pickle

#create chatbot with previously trained database
bot = ChatBot(
    'Medibot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///C:/Users/Lenovo/Desktop/MBA/HIM/database.sqlite3',
)

model_filename = 'C:/Users/Lenovo/Desktop/MBA/HIM/finalized_model_XGB.pkl'
loaded_model = pickle.load(open(model_filename, 'rb'))

dbName = 'C:/Users/Lenovo/Desktop/MBA/HIM/forms.sqlite3'
conn = sqlite3.connect(dbName)
#print("Opened database successfully")

conn.execute('CREATE TABLE IF NOT EXISTS forms (submissionCode TEXT, categoryCode INTEGER,Class_Demographics INTEGER,Class_Family_Planning INTEGER,Class_Infant_Health INTEGER,Class_Maternal_Behavior_Health INTEGER,Class_Maternal_Experiences INTEGER,Topic_Abuse_Physical INTEGER,Topic_Alcohol_Use INTEGER,Topic_Breastfeeding INTEGER,Topic_Contraception_Conception INTEGER, Topic_Income INTEGER,Topic_Mental_Health INTEGER,Topic_Morbidity_Infant INTEGER,Topic_Obesity INTEGER,Topic_Preconception_Morbidity INTEGER,Topic_Pregnancy_History INTEGER,Topic_Pregnancy_Intention INTEGER, Topic_Stress INTEGER, Topic_Tobacco_Use INTEGER,Response_NO INTEGER, Response_YES INTEGER, BOC_Adequacy_Prenatal_Care INTEGER,BOC_Birth_Weight INTEGER, BOC_Income INTEGER,BOC_Marital_Status INTEGER, BOC_Maternal_Age_3Levels INTEGER,BOC_Maternal_Age_4Levels INTEGER,BOC_Maternal_Age_Groupings INTEGER,BOC_Maternal_Age_Only INTEGER, BOC_Maternal_Education INTEGER,BOC_Maternal_Race INTEGER, BOC_Medicaid_Recipient INTEGER, BOC_None INTEGER,BOC_Previous_Live_Births INTEGER, BOC_WIC INTEGER,BOC_Pregnancy_Intendedness INTEGER, BOC_Smoked_Before INTEGER,BOC_Smoked_During INTEGER, Data_Value INTEGER,Low_Confidence_Limit INTEGER, High_Confidence_Limit INTEGER)')
conn.execute('CREATE TABLE IF NOT EXISTS results (submissionCode TEXT,prediction TEXT)')
conn.close()

app = Flask(__name__)

@app.route("/")
def home():    
    return render_template("home.html")

@app.route('/form')
def new_form():
   return render_template('form.html')

@app.route('/save',methods = ['POST'])
def save():
    try:
        submissionCode = time.time()
        
        age = int(request.form["age"])
        if age >= 20:
            BOC_Maternal_Age_Only = 0
        else:
            BOC_Maternal_Age_Only = 1
        
        #BOC_Maternal_Age_Only = request.form["age"]
        BOC_Maternal_Education = request.form["education"]
        BOC_Marital_Status = request.form["maritalSts"]
        BOC_Adequacy_Prenatal_Care = request.form["prenatal"]
        BOC_WIC = request.form["wic"]
        BOC_Medicaid_Recipient = request.form["medicaid"]
        BOC_Income = request.form["income"]
        BOC_Pregnancy_Intendedness = request.form["intention"]
        Contraception_Use = request.form["contraception"]
        BOC_Birth_Weight = request.form["lbw"]        
        Breastfeed = request.form["breastfeed"]
        Breastfeed_8 = request.form["breastfeed8"]
        BOC_Smoked_Before = request.form["smoking"]
        BOC_Smoked_During = request.form["smoking"]
        Drinking = request.form["drinking"]
        Anxiety = request.form["anxiety"]
        Heart_Problem = request.form["heart"]
        Obesity = request.form["obesity"]
        Miscarriage = request.form["miscarriage"]
        BOC_Previous_Live_Births = request.form["previousBirth"]
        Abuse = request.form["abuse"]
        Stress = request.form["stress"]
        
        BOC_Maternal_Age_3Levels = 0
        BOC_Maternal_Age_4Levels = 0
        BOC_Maternal_Age_Groupings = 0        
        BOC_Maternal_Race = 0        
        BOC_None = 0
        Data_Value = 0
        Low_Confidence_Limit = 85
        High_Confidence_Limit = 98
        query = ""
        predict = ""
        final = "Not depressed"
        totalWeightage = 0
        #weightage = {0:10,1:10,2:8,3:5,4:5,5:5,6:8,7:8,8:4,9:2,10:2,11:4,12:4,13:15,14:10}
        
        #calculate total weightage of answers
        if BOC_Income == "1":
            totalWeightage = totalWeightage + 10
        if BOC_Pregnancy_Intendedness == "1":
            totalWeightage = totalWeightage + 10
        if Contraception_Use == "1":
            totalWeightage = totalWeightage + 8
        if BOC_Birth_Weight == "1":
            totalWeightage = totalWeightage + 5 
        if Breastfeed == "1":
            totalWeightage = totalWeightage + 5
        if Breastfeed_8 == "1":
            totalWeightage = totalWeightage + 5
        if BOC_Smoked_Before == "1":
            totalWeightage = totalWeightage + 8
        if Drinking == "1":
            totalWeightage = totalWeightage + 8
        if Anxiety == "1":
            totalWeightage = totalWeightage + 4
        if Heart_Problem == "1":
            totalWeightage = totalWeightage + 2
        if Obesity == "1":
            totalWeightage = totalWeightage + 2
        if Miscarriage == "1":
            totalWeightage = totalWeightage + 4
        if BOC_Previous_Live_Births == "1":
            totalWeightage = totalWeightage + 4
        if Abuse == "1":
            totalWeightage = totalWeightage + 15
        if Stress == "1":
            totalWeightage = totalWeightage + 10
                            
        with sqlite3.connect(dbName) as con:
            cur = con.cursor()
            
            # Income
            cur.execute("INSERT INTO forms (submissionCode,categoryCode,'Class_Demographics', 'Class_Family_Planning', 'Class_Infant_Health','Class_Maternal_Behavior_Health', 'Class_Maternal_Experiences','Topic_Abuse_Physical', 'Topic_Alcohol_Use', 'Topic_Breastfeeding','Topic_Contraception_Conception', 'Topic_Income','Topic_Mental_Health', 'Topic_Morbidity_Infant', 'Topic_Obesity','Topic_Preconception_Morbidity', 'Topic_Pregnancy_History','Topic_Pregnancy_Intention', 'Topic_Stress', 'Topic_Tobacco_Use','Response_NO', 'Response_YES', 'BOC_Adequacy_Prenatal_Care','BOC_Birth_Weight', 'BOC_Income','BOC_Marital_Status', 'BOC_Maternal_Age_3Levels','BOC_Maternal_Age_4Levels','BOC_Maternal_Age_Groupings','BOC_Maternal_Age_Only', 'BOC_Maternal_Education','BOC_Maternal_Race', 'BOC_Medicaid_Recipient', 'BOC_None','BOC_Previous_Live_Births', 'BOC_WIC','BOC_Pregnancy_Intendedness', 'BOC_Smoked_Before','BOC_Smoked_During', 'Data_Value','Low_Confidence_Limit', 'High_Confidence_Limit') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(submissionCode,0, 1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,int(not BOC_Income), BOC_Income,BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit ))
            
            # Pregnancy intendness
            cur.execute("INSERT INTO forms (submissionCode,categoryCode,'Class_Demographics', 'Class_Family_Planning', 'Class_Infant_Health','Class_Maternal_Behavior_Health', 'Class_Maternal_Experiences','Topic_Abuse_Physical', 'Topic_Alcohol_Use', 'Topic_Breastfeeding','Topic_Contraception_Conception', 'Topic_Income','Topic_Mental_Health', 'Topic_Morbidity_Infant', 'Topic_Obesity','Topic_Preconception_Morbidity', 'Topic_Pregnancy_History','Topic_Pregnancy_Intention', 'Topic_Stress', 'Topic_Tobacco_Use','Response_NO', 'Response_YES', 'BOC_Adequacy_Prenatal_Care','BOC_Birth_Weight', 'BOC_Income','BOC_Marital_Status', 'BOC_Maternal_Age_3Levels','BOC_Maternal_Age_4Levels','BOC_Maternal_Age_Groupings','BOC_Maternal_Age_Only', 'BOC_Maternal_Education','BOC_Maternal_Race', 'BOC_Medicaid_Recipient', 'BOC_None','BOC_Previous_Live_Births', 'BOC_WIC','BOC_Pregnancy_Intendedness', 'BOC_Smoked_Before','BOC_Smoked_During', 'Data_Value','Low_Confidence_Limit', 'High_Confidence_Limit') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(submissionCode,1, 0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,int(not BOC_Pregnancy_Intendedness), BOC_Pregnancy_Intendedness,BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit ))
            
            # Contraception use
            cur.execute("INSERT INTO forms (submissionCode,categoryCode,'Class_Demographics', 'Class_Family_Planning', 'Class_Infant_Health','Class_Maternal_Behavior_Health', 'Class_Maternal_Experiences','Topic_Abuse_Physical', 'Topic_Alcohol_Use', 'Topic_Breastfeeding','Topic_Contraception_Conception', 'Topic_Income','Topic_Mental_Health', 'Topic_Morbidity_Infant', 'Topic_Obesity','Topic_Preconception_Morbidity', 'Topic_Pregnancy_History','Topic_Pregnancy_Intention', 'Topic_Stress', 'Topic_Tobacco_Use','Response_NO', 'Response_YES', 'BOC_Adequacy_Prenatal_Care','BOC_Birth_Weight', 'BOC_Income','BOC_Marital_Status', 'BOC_Maternal_Age_3Levels','BOC_Maternal_Age_4Levels','BOC_Maternal_Age_Groupings','BOC_Maternal_Age_Only', 'BOC_Maternal_Education','BOC_Maternal_Race', 'BOC_Medicaid_Recipient', 'BOC_None','BOC_Previous_Live_Births', 'BOC_WIC','BOC_Pregnancy_Intendedness', 'BOC_Smoked_Before','BOC_Smoked_During', 'Data_Value','Low_Confidence_Limit', 'High_Confidence_Limit') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(submissionCode,2, 0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,int(not Contraception_Use), Contraception_Use,BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit ))

            # Birth weight
            cur.execute("INSERT INTO forms (submissionCode,categoryCode,'Class_Demographics', 'Class_Family_Planning', 'Class_Infant_Health','Class_Maternal_Behavior_Health', 'Class_Maternal_Experiences','Topic_Abuse_Physical', 'Topic_Alcohol_Use', 'Topic_Breastfeeding','Topic_Contraception_Conception', 'Topic_Income','Topic_Mental_Health', 'Topic_Morbidity_Infant', 'Topic_Obesity','Topic_Preconception_Morbidity', 'Topic_Pregnancy_History','Topic_Pregnancy_Intention', 'Topic_Stress', 'Topic_Tobacco_Use','Response_NO', 'Response_YES', 'BOC_Adequacy_Prenatal_Care','BOC_Birth_Weight', 'BOC_Income','BOC_Marital_Status', 'BOC_Maternal_Age_3Levels','BOC_Maternal_Age_4Levels','BOC_Maternal_Age_Groupings','BOC_Maternal_Age_Only', 'BOC_Maternal_Education','BOC_Maternal_Race', 'BOC_Medicaid_Recipient', 'BOC_None','BOC_Previous_Live_Births', 'BOC_WIC','BOC_Pregnancy_Intendedness', 'BOC_Smoked_Before','BOC_Smoked_During', 'Data_Value','Low_Confidence_Limit', 'High_Confidence_Limit') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(submissionCode,3, 0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,int(not BOC_Birth_Weight), BOC_Birth_Weight,BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit ))
            
            # Breastfeeding
            cur.execute("INSERT INTO forms (submissionCode,categoryCode,'Class_Demographics', 'Class_Family_Planning', 'Class_Infant_Health','Class_Maternal_Behavior_Health', 'Class_Maternal_Experiences','Topic_Abuse_Physical', 'Topic_Alcohol_Use', 'Topic_Breastfeeding','Topic_Contraception_Conception', 'Topic_Income','Topic_Mental_Health', 'Topic_Morbidity_Infant', 'Topic_Obesity','Topic_Preconception_Morbidity', 'Topic_Pregnancy_History','Topic_Pregnancy_Intention', 'Topic_Stress', 'Topic_Tobacco_Use','Response_NO', 'Response_YES', 'BOC_Adequacy_Prenatal_Care','BOC_Birth_Weight', 'BOC_Income','BOC_Marital_Status', 'BOC_Maternal_Age_3Levels','BOC_Maternal_Age_4Levels','BOC_Maternal_Age_Groupings','BOC_Maternal_Age_Only', 'BOC_Maternal_Education','BOC_Maternal_Race', 'BOC_Medicaid_Recipient', 'BOC_None','BOC_Previous_Live_Births', 'BOC_WIC','BOC_Pregnancy_Intendedness', 'BOC_Smoked_Before','BOC_Smoked_During', 'Data_Value','Low_Confidence_Limit', 'High_Confidence_Limit') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(submissionCode,4, 0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,int(not Breastfeed), Breastfeed,BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit ))

            # Breastfeeding after 8 weeks
            cur.execute("INSERT INTO forms (submissionCode,categoryCode,'Class_Demographics', 'Class_Family_Planning', 'Class_Infant_Health','Class_Maternal_Behavior_Health', 'Class_Maternal_Experiences','Topic_Abuse_Physical', 'Topic_Alcohol_Use', 'Topic_Breastfeeding','Topic_Contraception_Conception', 'Topic_Income','Topic_Mental_Health', 'Topic_Morbidity_Infant', 'Topic_Obesity','Topic_Preconception_Morbidity', 'Topic_Pregnancy_History','Topic_Pregnancy_Intention', 'Topic_Stress', 'Topic_Tobacco_Use','Response_NO', 'Response_YES', 'BOC_Adequacy_Prenatal_Care','BOC_Birth_Weight', 'BOC_Income','BOC_Marital_Status', 'BOC_Maternal_Age_3Levels','BOC_Maternal_Age_4Levels','BOC_Maternal_Age_Groupings','BOC_Maternal_Age_Only', 'BOC_Maternal_Education','BOC_Maternal_Race', 'BOC_Medicaid_Recipient', 'BOC_None','BOC_Previous_Live_Births', 'BOC_WIC','BOC_Pregnancy_Intendedness', 'BOC_Smoked_Before','BOC_Smoked_During', 'Data_Value','Low_Confidence_Limit', 'High_Confidence_Limit') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(submissionCode,5, 0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,int(not Breastfeed_8), Breastfeed_8,BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit ))
            
            # Smoking
            cur.execute("INSERT INTO forms (submissionCode,categoryCode,'Class_Demographics', 'Class_Family_Planning', 'Class_Infant_Health','Class_Maternal_Behavior_Health', 'Class_Maternal_Experiences','Topic_Abuse_Physical', 'Topic_Alcohol_Use', 'Topic_Breastfeeding','Topic_Contraception_Conception', 'Topic_Income','Topic_Mental_Health', 'Topic_Morbidity_Infant', 'Topic_Obesity','Topic_Preconception_Morbidity', 'Topic_Pregnancy_History','Topic_Pregnancy_Intention', 'Topic_Stress', 'Topic_Tobacco_Use','Response_NO', 'Response_YES', 'BOC_Adequacy_Prenatal_Care','BOC_Birth_Weight', 'BOC_Income','BOC_Marital_Status', 'BOC_Maternal_Age_3Levels','BOC_Maternal_Age_4Levels','BOC_Maternal_Age_Groupings','BOC_Maternal_Age_Only', 'BOC_Maternal_Education','BOC_Maternal_Race', 'BOC_Medicaid_Recipient', 'BOC_None','BOC_Previous_Live_Births', 'BOC_WIC','BOC_Pregnancy_Intendedness', 'BOC_Smoked_Before','BOC_Smoked_During', 'Data_Value','Low_Confidence_Limit', 'High_Confidence_Limit') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(submissionCode,6, 0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,int(not BOC_Smoked_Before), BOC_Smoked_Before,BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit ))
            
            # Drinking
            cur.execute("INSERT INTO forms (submissionCode,categoryCode,'Class_Demographics', 'Class_Family_Planning', 'Class_Infant_Health','Class_Maternal_Behavior_Health', 'Class_Maternal_Experiences','Topic_Abuse_Physical', 'Topic_Alcohol_Use', 'Topic_Breastfeeding','Topic_Contraception_Conception', 'Topic_Income','Topic_Mental_Health', 'Topic_Morbidity_Infant', 'Topic_Obesity','Topic_Preconception_Morbidity', 'Topic_Pregnancy_History','Topic_Pregnancy_Intention', 'Topic_Stress', 'Topic_Tobacco_Use','Response_NO', 'Response_YES', 'BOC_Adequacy_Prenatal_Care','BOC_Birth_Weight', 'BOC_Income','BOC_Marital_Status', 'BOC_Maternal_Age_3Levels','BOC_Maternal_Age_4Levels','BOC_Maternal_Age_Groupings','BOC_Maternal_Age_Only', 'BOC_Maternal_Education','BOC_Maternal_Race', 'BOC_Medicaid_Recipient', 'BOC_None','BOC_Previous_Live_Births', 'BOC_WIC','BOC_Pregnancy_Intendedness', 'BOC_Smoked_Before','BOC_Smoked_During', 'Data_Value','Low_Confidence_Limit', 'High_Confidence_Limit') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(submissionCode,7, 0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,int(not Drinking), Drinking,BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit ))
            
            # Anxiety
            cur.execute("INSERT INTO forms (submissionCode,categoryCode,'Class_Demographics', 'Class_Family_Planning', 'Class_Infant_Health','Class_Maternal_Behavior_Health', 'Class_Maternal_Experiences','Topic_Abuse_Physical', 'Topic_Alcohol_Use', 'Topic_Breastfeeding','Topic_Contraception_Conception', 'Topic_Income','Topic_Mental_Health', 'Topic_Morbidity_Infant', 'Topic_Obesity','Topic_Preconception_Morbidity', 'Topic_Pregnancy_History','Topic_Pregnancy_Intention', 'Topic_Stress', 'Topic_Tobacco_Use','Response_NO', 'Response_YES', 'BOC_Adequacy_Prenatal_Care','BOC_Birth_Weight', 'BOC_Income','BOC_Marital_Status', 'BOC_Maternal_Age_3Levels','BOC_Maternal_Age_4Levels','BOC_Maternal_Age_Groupings','BOC_Maternal_Age_Only', 'BOC_Maternal_Education','BOC_Maternal_Race', 'BOC_Medicaid_Recipient', 'BOC_None','BOC_Previous_Live_Births', 'BOC_WIC','BOC_Pregnancy_Intendedness', 'BOC_Smoked_Before','BOC_Smoked_During', 'Data_Value','Low_Confidence_Limit', 'High_Confidence_Limit') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(submissionCode,8, 0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,int(not Anxiety), Anxiety,BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit ))

            # Heart problem
            cur.execute("INSERT INTO forms (submissionCode,categoryCode,'Class_Demographics', 'Class_Family_Planning', 'Class_Infant_Health','Class_Maternal_Behavior_Health', 'Class_Maternal_Experiences','Topic_Abuse_Physical', 'Topic_Alcohol_Use', 'Topic_Breastfeeding','Topic_Contraception_Conception', 'Topic_Income','Topic_Mental_Health', 'Topic_Morbidity_Infant', 'Topic_Obesity','Topic_Preconception_Morbidity', 'Topic_Pregnancy_History','Topic_Pregnancy_Intention', 'Topic_Stress', 'Topic_Tobacco_Use','Response_NO', 'Response_YES', 'BOC_Adequacy_Prenatal_Care','BOC_Birth_Weight', 'BOC_Income','BOC_Marital_Status', 'BOC_Maternal_Age_3Levels','BOC_Maternal_Age_4Levels','BOC_Maternal_Age_Groupings','BOC_Maternal_Age_Only', 'BOC_Maternal_Education','BOC_Maternal_Race', 'BOC_Medicaid_Recipient', 'BOC_None','BOC_Previous_Live_Births', 'BOC_WIC','BOC_Pregnancy_Intendedness', 'BOC_Smoked_Before','BOC_Smoked_During', 'Data_Value','Low_Confidence_Limit', 'High_Confidence_Limit') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(submissionCode,9, 0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,int(not Heart_Problem), Heart_Problem,BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit ))
            
            # Obesity
            cur.execute("INSERT INTO forms (submissionCode,categoryCode,'Class_Demographics', 'Class_Family_Planning', 'Class_Infant_Health','Class_Maternal_Behavior_Health', 'Class_Maternal_Experiences','Topic_Abuse_Physical', 'Topic_Alcohol_Use', 'Topic_Breastfeeding','Topic_Contraception_Conception', 'Topic_Income','Topic_Mental_Health', 'Topic_Morbidity_Infant', 'Topic_Obesity','Topic_Preconception_Morbidity', 'Topic_Pregnancy_History','Topic_Pregnancy_Intention', 'Topic_Stress', 'Topic_Tobacco_Use','Response_NO', 'Response_YES', 'BOC_Adequacy_Prenatal_Care','BOC_Birth_Weight', 'BOC_Income','BOC_Marital_Status', 'BOC_Maternal_Age_3Levels','BOC_Maternal_Age_4Levels','BOC_Maternal_Age_Groupings','BOC_Maternal_Age_Only', 'BOC_Maternal_Education','BOC_Maternal_Race', 'BOC_Medicaid_Recipient', 'BOC_None','BOC_Previous_Live_Births', 'BOC_WIC','BOC_Pregnancy_Intendedness', 'BOC_Smoked_Before','BOC_Smoked_During', 'Data_Value','Low_Confidence_Limit', 'High_Confidence_Limit') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(submissionCode,10, 0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,int(not Obesity), Obesity,BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit ))

            # Miscarriage/ death
            cur.execute("INSERT INTO forms (submissionCode,categoryCode,'Class_Demographics', 'Class_Family_Planning', 'Class_Infant_Health','Class_Maternal_Behavior_Health', 'Class_Maternal_Experiences','Topic_Abuse_Physical', 'Topic_Alcohol_Use', 'Topic_Breastfeeding','Topic_Contraception_Conception', 'Topic_Income','Topic_Mental_Health', 'Topic_Morbidity_Infant', 'Topic_Obesity','Topic_Preconception_Morbidity', 'Topic_Pregnancy_History','Topic_Pregnancy_Intention', 'Topic_Stress', 'Topic_Tobacco_Use','Response_NO', 'Response_YES', 'BOC_Adequacy_Prenatal_Care','BOC_Birth_Weight', 'BOC_Income','BOC_Marital_Status', 'BOC_Maternal_Age_3Levels','BOC_Maternal_Age_4Levels','BOC_Maternal_Age_Groupings','BOC_Maternal_Age_Only', 'BOC_Maternal_Education','BOC_Maternal_Race', 'BOC_Medicaid_Recipient', 'BOC_None','BOC_Previous_Live_Births', 'BOC_WIC','BOC_Pregnancy_Intendedness', 'BOC_Smoked_Before','BOC_Smoked_During', 'Data_Value','Low_Confidence_Limit', 'High_Confidence_Limit') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(submissionCode,11, 0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,int(not Miscarriage), Miscarriage,BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit ))
            
            # Previous pregnancy LBW
            cur.execute("INSERT INTO forms (submissionCode,categoryCode,'Class_Demographics', 'Class_Family_Planning', 'Class_Infant_Health','Class_Maternal_Behavior_Health', 'Class_Maternal_Experiences','Topic_Abuse_Physical', 'Topic_Alcohol_Use', 'Topic_Breastfeeding','Topic_Contraception_Conception', 'Topic_Income','Topic_Mental_Health', 'Topic_Morbidity_Infant', 'Topic_Obesity','Topic_Preconception_Morbidity', 'Topic_Pregnancy_History','Topic_Pregnancy_Intention', 'Topic_Stress', 'Topic_Tobacco_Use','Response_NO', 'Response_YES', 'BOC_Adequacy_Prenatal_Care','BOC_Birth_Weight', 'BOC_Income','BOC_Marital_Status', 'BOC_Maternal_Age_3Levels','BOC_Maternal_Age_4Levels','BOC_Maternal_Age_Groupings','BOC_Maternal_Age_Only', 'BOC_Maternal_Education','BOC_Maternal_Race', 'BOC_Medicaid_Recipient', 'BOC_None','BOC_Previous_Live_Births', 'BOC_WIC','BOC_Pregnancy_Intendedness', 'BOC_Smoked_Before','BOC_Smoked_During', 'Data_Value','Low_Confidence_Limit', 'High_Confidence_Limit') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(submissionCode,12, 0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,int(not BOC_Previous_Live_Births), BOC_Previous_Live_Births,BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit ))

            # Physical abuse
            cur.execute("INSERT INTO forms (submissionCode,categoryCode,'Class_Demographics', 'Class_Family_Planning', 'Class_Infant_Health','Class_Maternal_Behavior_Health', 'Class_Maternal_Experiences','Topic_Abuse_Physical', 'Topic_Alcohol_Use', 'Topic_Breastfeeding','Topic_Contraception_Conception', 'Topic_Income','Topic_Mental_Health', 'Topic_Morbidity_Infant', 'Topic_Obesity','Topic_Preconception_Morbidity', 'Topic_Pregnancy_History','Topic_Pregnancy_Intention', 'Topic_Stress', 'Topic_Tobacco_Use','Response_NO', 'Response_YES', 'BOC_Adequacy_Prenatal_Care','BOC_Birth_Weight', 'BOC_Income','BOC_Marital_Status', 'BOC_Maternal_Age_3Levels','BOC_Maternal_Age_4Levels','BOC_Maternal_Age_Groupings','BOC_Maternal_Age_Only', 'BOC_Maternal_Education','BOC_Maternal_Race', 'BOC_Medicaid_Recipient', 'BOC_None','BOC_Previous_Live_Births', 'BOC_WIC','BOC_Pregnancy_Intendedness', 'BOC_Smoked_Before','BOC_Smoked_During', 'Data_Value','Low_Confidence_Limit', 'High_Confidence_Limit') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(submissionCode,13, 0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,int(not Abuse), Abuse,BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit ))
            
            # Stress
            cur.execute("INSERT INTO forms (submissionCode,categoryCode,'Class_Demographics', 'Class_Family_Planning', 'Class_Infant_Health','Class_Maternal_Behavior_Health', 'Class_Maternal_Experiences','Topic_Abuse_Physical', 'Topic_Alcohol_Use', 'Topic_Breastfeeding','Topic_Contraception_Conception', 'Topic_Income','Topic_Mental_Health', 'Topic_Morbidity_Infant', 'Topic_Obesity','Topic_Preconception_Morbidity', 'Topic_Pregnancy_History','Topic_Pregnancy_Intention', 'Topic_Stress', 'Topic_Tobacco_Use','Response_NO', 'Response_YES', 'BOC_Adequacy_Prenatal_Care','BOC_Birth_Weight', 'BOC_Income','BOC_Marital_Status', 'BOC_Maternal_Age_3Levels','BOC_Maternal_Age_4Levels','BOC_Maternal_Age_Groupings','BOC_Maternal_Age_Only', 'BOC_Maternal_Education','BOC_Maternal_Race', 'BOC_Medicaid_Recipient', 'BOC_None','BOC_Previous_Live_Births', 'BOC_WIC','BOC_Pregnancy_Intendedness', 'BOC_Smoked_Before','BOC_Smoked_During', 'Data_Value','Low_Confidence_Limit', 'High_Confidence_Limit') VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(submissionCode,14, 0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,int(not Stress), Stress,BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit ))

            con.commit()
            
            query = "select Class_Demographics,Class_Family_Planning,Class_Infant_Health,Class_Maternal_Behavior_Health,Class_Maternal_Experiences,Topic_Abuse_Physical,Topic_Alcohol_Use,Topic_Breastfeeding,Topic_Contraception_Conception, Topic_Income,Topic_Mental_Health,Topic_Morbidity_Infant,Topic_Obesity,Topic_Preconception_Morbidity,Topic_Pregnancy_History,Topic_Pregnancy_Intention, Topic_Stress, Topic_Tobacco_Use,Response_NO, Response_YES, BOC_Adequacy_Prenatal_Care,BOC_Birth_Weight, BOC_Income,BOC_Marital_Status, BOC_Maternal_Age_3Levels,BOC_Maternal_Age_4Levels,BOC_Maternal_Age_Groupings,BOC_Maternal_Age_Only, BOC_Maternal_Education,BOC_Maternal_Race, BOC_Medicaid_Recipient, BOC_None,BOC_Previous_Live_Births, BOC_WIC,BOC_Pregnancy_Intendedness, BOC_Smoked_Before,BOC_Smoked_During, Data_Value,Low_Confidence_Limit, High_Confidence_Limit from forms where submissionCode ={} and categoryCode=4 order by categoryCode asc".format(submissionCode)
            
            df = pd.read_sql_query(query, con)
            y  =  df[["Response_NO",  "Response_YES"]]
            X  =  df.drop(columns=["Response_NO",  "Response_YES"])
            sc = StandardScaler()
            X  =  sc.fit_transform(X)
            y  =  y.drop(["Response_NO"],  axis=1)
            y  =  np.array(y)
            
            presults = {}
            counter = 0
            
            for i in range(len(X)):                
                single_data = X[i]
                single_data  =  single_data.reshape((-1,  38))
                predict = "Depressed" if loaded_model.predict(single_data) == 1 else "Not Depressed"
                presults[i] = predict                
                if predict == "Depressed":
                    counter = counter + 1
                 #   break
            
            #save the result in db
            if totalWeightage >= 50:
                final = "Depressed"
            elif totalWeightage in range(30,50):
                final = "Possibly Depressed"
            elif counter > 9:
                final = "Depressed"
                
            cur.execute("INSERT INTO results (submissionCode, prediction) VALUES (?,?)",(submissionCode, final))

            con.commit()
    except:
        msg = str(sys.exc_info()[0])
        #msg = "error"
    finally:
        return render_template("result.html", msg = final)
        con.close()
     #redirect(url_for('result',msg = msg))

# @app.route("/result")
# def result():    
#     scode = request.args.get('msg')
#     if msg != "error":
#         #get prediction result
#         con = sqlite3.connect(dbName)
#         df = pd.read_sql_query("SELECT * from forms where submissionCode = " + scode, con)
#         y  =  df[["Response_NO",  "Response_YES"]]
#         X  =  df.drop(columns=["Response_NO",  "Response_YES"])
#         sc = StandardScaler()
#         X  =  sc.fit_transform(X)
#         y  =  y.drop(["Response_NO"],  axis=1)
#         y  =  np.array(y)
#         
#         #single_data = 
#         #single_data  =  single_data.reshape((-1,  38))
# 
#         return render_template("result.html",msg = len(X))
#     else:
#         return render_template("result.html",msg="prediction error")

@app.route("/get")
def get_bot_response():    
    userText = request.args.get('msg')    
    return str(bot.get_response(userText))


if __name__ == "__main__":    
    app.run(debug=False)