from django.shortcuts import render, redirect
import pandas as pd
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from jupyterlab_widgets import data
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import mysql.connector
import hashlib
from datetime import datetime
import time
import plotly.graph_objects as go
from plotly.offline import plot

id = 0
curtime = time.time()

data = pd.read_csv(r'C:\Users\Asus\Desktop\DiabetesPrediction\DiabetesAnalysis.csv')
X = data.drop(['Outcome'], axis=1)
Y = data['Outcome']
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.30)

model = LogisticRegression(solver='liblinear')
model.fit(X_train, Y_train)
print(model.score(X_test, Y_test))


mydb = mysql.connector.connect(
    host="localhost",
    user="Amir1602",
    password="Amir12345@",
    database="diabetesprediction"
)
mycursor = mydb.cursor()


def home(request):
    global error
    error = request
    return render(request, 'home.html')


@csrf_protect
def predict(request):
    global id
    lattime = time.time()
    if (lattime - curtime < 300 and id != 0):
        return render(request, 'predict.html', None)
    else:
        id = 0
        return redirect('/')


def login(request):
    global id
    global curtime
    username = request.POST['username']
    password = hashlib.md5(request.POST['pass'].encode()).hexdigest()

    sql = "SELECT * FROM user where username = %s and password = %s"
    value = (username, password)
    mycursor.execute(sql, value)
    result = mycursor.fetchall()

    if (username != "" and password != ""):
        if (len(result) == 1):
            if (result[0][4] == 0):
                id = 1
                return redirect('/viewadmin')

            elif (result[0][4] == 1):
                id = result[0][0]
                curtime = time.time()
                return render(request, 'predict.html', {"message": "Welcome " + str(result[0][1]), "alert": "alert("})
            else:
                return render(request, 'home.html', {"message": "Invalid", "alert": "alert("})
        else:
            return render(request, 'home.html', {"message": "Invalid", "alert": "alert("})
    return render(request, 'home.html', {"message": "Wrong username or password", "alert": "alert("})


def signup(request):
    username = request.POST['username']
    password = request.POST['pass']
    rpassword = request.POST['repass']
    email = request.POST['email']
    if (username != "" and password != "" and rpassword != "" and email != ""):
        if (password == rpassword):
            sql = "INSERT INTO `user`(`id`, `username`, `password`, `email`, `status`) VALUES (NULL, %s, %s, %s, '1')"
            value = (username, hashlib.md5(password.encode()).hexdigest(), email)
            mycursor.execute(sql, value)
            mydb.commit()
            if (mycursor.rowcount == 1):
                return render(request, 'home.html', {"message": "Account Created Successfully", "alert": "alert("})
            else:
                return render(request, 'home.html', {"message": "Failed to Create Account", "alert": "alert("})
        else:
            return render(request, 'home.html',
                          {"message": "Password and Repeat Password is not same", "alert": "alert("})
    else:
        return render(request, 'home.html', {"message": "Please fill out all detail", "alert": "alert("})


def viewdata(request):
    global id
    lattime = time.time()
    if (lattime - curtime < 300 and id != 0):
        dateupd = datetime.now().strftime('%Y-%m')
        yea = dateupd.split('-')[0]
        mont = dateupd.split('-')[1]
        result = getresult(id, yea, mont)

        datetimearr = []
        r_diab = []
        gluc = []
        b_pres = []
        insul = []
        bmi = []
        table = ""
        if(len(result) != 0):
            datetimearr = result[:, 6]
            r_diab = result[:, 5]
            gluc = result[:, 1]
            b_pres = result[:, 2]
            insul = result[:, 3]
            bmi = result[:, 4]
            for i in range(len(result)):
                table += '<tr>'
                table += '<td>' + str(i + 1) + '</td>'
                table += '<td>' + str(result[i][6]) + '</td>'
                table += '<td>' + str(result[i][1]) + '</td>'
                table += '<td>' + str(result[i][2]) + '</td>'
                table += '<td>' + str(result[i][3]) + '</td>'
                table += '<td>' + str(result[i][4]) + '</td>'
                table += '<td>' + str(result[i][5]) + '</td>'
                table += '</tr>'

        plot1 = getgraph(r_diab, datetimearr, yea, mont, 'Result Diabetes', [0, 1])
        plot2 = getgraph(gluc, datetimearr, yea, mont, 'Glucose Level', [0, 200])
        plot3 = getgraph(b_pres, datetimearr, yea, mont, 'Blood Pressure', [0, 200])
        plot4 = getgraph(insul, datetimearr, yea, mont, 'Insulin', [0, 1000])
        plot5 = getgraph(bmi, datetimearr, yea, mont, 'BMI', [0, 100])

        return render(request, 'viewdata.html',
                      {"dateupd": dateupd, "plot_div1": plot1, "plot_div2": plot2, "plot_div3": plot3,
                       "plot_div4": plot4, "plot_div5": plot5, "table": table})
    else:
        id = 0
        return redirect('/')

def info(request):
    global id
    lattime = time.time()
    if (lattime - curtime < 300 and id != 0):
        return render(request, 'info.html', None)
    else:
        id = 0
        return redirect('/')



def viewing(request):
    global id
    lattime = time.time()
    if (lattime - curtime < 300 and id != 0):
        dateupd = request.POST['datetaker']
        print(dateupd)
        yea = dateupd.split('-')[0]
        mont = dateupd.split('-')[1]
        result = getresult(id, yea, mont)

        datetimearr = []
        r_diab = []
        gluc = []
        b_pres = []
        insul = []
        bmi = []
        table = ""
        if(len(result) != 0):
            datetimearr = result[:, 6]
            r_diab = result[:, 5]
            gluc = result[:, 1]
            b_pres = result[:, 2]
            insul = result[:, 3]
            bmi = result[:, 4]
            for i in range(len(result)):
                table += '<tr>'
                table += '<td>' + str(i + 1) + '</td>'
                table += '<td>' + str(result[i][6]) + '</td>'
                table += '<td>' + str(result[i][1]) + '</td>'
                table += '<td>' + str(result[i][2]) + '</td>'
                table += '<td>' + str(result[i][3]) + '</td>'
                table += '<td>' + str(result[i][4]) + '</td>'
                table += '<td>' + str(result[i][5]) + '</td>'
                table += '</tr>'

        plot1 = getgraph(r_diab, datetimearr, yea, mont, 'Result Diabetes', [0, 1])
        plot2 = getgraph(gluc, datetimearr, yea, mont, 'Glucose Level', [0, 200])
        plot3 = getgraph(b_pres, datetimearr, yea, mont, 'Blood Pressure', [0, 200])
        plot4 = getgraph(insul, datetimearr, yea, mont, 'Insulin', [0, 1000])
        plot5 = getgraph(bmi, datetimearr, yea, mont, 'BMI', [0, 100])

        return render(request, 'viewdata.html',
                      {"dateupd": dateupd, "plot_div1": plot1, "plot_div2": plot2, "plot_div3": plot3,
                       "plot_div4": plot4, "plot_div5": plot5, "table": table})
    else:
        id = 0
        return redirect('/')

def viewadmin(request):
    global id
    lattime = time.time()
    if (lattime - curtime < 300 and id != 0):
        dateupd = datetime.now().strftime('%Y-%m')
        yea = dateupd.split('-')[0]
        mont = dateupd.split('-')[1]
        result = getresultadmin(yea, mont)
        positive = []
        negative = []
        datetimearr = []
        table = ""
        if(len(result) != 0):
            for i in result:
                datetimearr.append(str(i[6]).split()[0])
                print(str(i[6]))
            datetimearr = list(dict.fromkeys(datetimearr))
            positive = np.zeros(len(datetimearr)).tolist()
            negative = np.zeros(len(datetimearr)).tolist()
            for i in result:
                for j in range(len(datetimearr)):
                    date = str(i[6]).split()[0]
                    if(date == datetimearr[j]):
                        if(i[5] == 1):
                            positive[j] += 1
                            break
                        else:
                            negative[j] += 1
                            break
            for i in range(len(datetimearr)):
                table += '<tr>'
                table += '<td>' + str(i + 1) + '</td>'
                table += '<td>' + str(datetimearr[i]) + '</td>'
                table += '<td>' + str(positive[i]) + '</td>'
                table += '<td>' + str(negative[i]) + '</td>'
                table += '</tr>'

        plot1 = getgraph2(positive, datetimearr, negative, yea, mont, 'Diabetes', 'Positive', 'Negative', [0, 100])

        return render(request, 'viewadmin.html',
                      {"dateupd": dateupd, "plot_div1": plot1, "table": table})
    else:
        id = 0
        return redirect('/')


def viewingadmin(request):
    global id
    lattime = time.time()
    if (lattime - curtime < 300 and id != 0):
        dateupd = request.POST['datetaker']
        print(dateupd)
        yea = dateupd.split('-')[0]
        mont = dateupd.split('-')[1]
        result = getresultadmin(yea, mont)

        positive = []
        negative = []
        datetimearr = []
        table = ""
        if(len(result) != 0):
            for i in result:
                datetimearr.append(str(i[6]).split()[0])
            datetimearr = list(dict.fromkeys(datetimearr))
            positive = np.zeros(len(datetimearr)).tolist()
            negative = np.zeros(len(datetimearr)).tolist()
            for i in result:
                date = str(i[6]).split()[0]
                for j in range(len(datetimearr)):
                    if (date == datetimearr[j]):
                        if (i[5] == 1):
                            positive[j] += 1
                            break
                        else:
                            negative[j] += 1
                            break

            for i in range(len(datetimearr)):
                table += '<tr>'
                table += '<td>' + str(i + 1) + '</td>'
                table += '<td>' + str(datetimearr[i]) + '</td>'
                table += '<td>' + str(positive[i]) + '</td>'
                table += '<td>' + str(negative[i]) + '</td>'
                table += '</tr>'

        plot1 = getgraph2(positive, datetimearr, negative, yea, mont, 'Diabetes', 'Have Diabetes', 'Do Not Have Diabetes', [0, 100])

        return render(request, 'viewadmin.html',
                      {"dateupd": dateupd, "plot_div1": plot1, "table": table})
    else:
        id = 0
        return redirect('/')

def getresult(ids, yea, mont):
    sql = "SELECT * FROM record where user_id = %s and YEAR(datetime) = %s AND MONTH(datetime) = %s"
    value = (ids, yea, mont)
    mycursor.execute(sql, value)
    result = mycursor.fetchall()
    return np.array(result)

def getresultadmin(yea, mont):
    sql = "SELECT * FROM record where YEAR(datetime) = %s AND MONTH(datetime) = %s"
    value = (yea, mont)
    mycursor.execute(sql, value)
    result = mycursor.fetchall()
    return np.array(result)

def getgraph(a, b, yea, mont, title, aa):
    next = int(mont) + 1
    nyea = yea
    if (next < 10):
        nmont = '0' + str(next)
    elif (next == 13):
        nyea = str(int(yea) + 1)
        nmont = '01'
    else:
        nmont = str(next)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=b, y=a))
    return plot(fig.update_layout(xaxis_range=[yea + '-' + mont, nyea + '-' + nmont], yaxis_range=aa, title_text=title),
                output_type='div')

def getgraph2(a, b, c, yea, mont, title, ta, tb, aa):
    next = int(mont) + 1
    nyea = yea
    if (next < 10):
        nmont = '0' + str(next)
    elif (next == 13):
        nyea = str(int(yea) + 1)
        nmont = '01'
    else:
        nmont = str(next)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=b, y=a, name= ta))
    fig.add_trace(go.Scatter(x=b, y=c, name= tb))
    return plot(fig.update_layout(xaxis_range=[yea + '-' + mont, nyea + '-' + nmont], yaxis_range=aa, title_text=title),
                output_type='div')

def result(request):
    global id
    lattime = time.time()
    if (lattime - curtime < 300 and id != 0):
        val1 = float(request.POST['n1'])
        val2 = float(request.POST['n2'])
        val3 = float(request.POST['n3'])
        val4 = float(request.POST['n4'])

        pred = model.predict([[val1, val2, val3, val4]])
        val5 = 0
        result1 = ""
        if pred == [1]:
            result1 = "Yes"
            val5 = 1
        else:
            result1 = "No"
        curdatetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO `record`(`id`, `gluc`, `b_press`, `insulin`, `bmi`, `result`, `datetime`, `user_id`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)"
        value = (val1, val2, val3, val4, val5, curdatetime, id)
        mycursor.execute(sql, value)
        mydb.commit()
        if (mycursor.rowcount == 1):
            return render(request, "predict.html",
                          {"result5": result1, "result1": val1, "result2": val2, "result3": val3, "result4": val4, "message": "New Data Update Successfully", "alert": "alert("})
        else:
            return render(request, 'predict.html',
                          {"result5": result1, "result1": val1, "result2": val2, "result3": val3, "result4": val4, "message": "Failed to Update Data", "alert": "alert("})

    else:
        id = 0
        return redirect('/')


def profile(request):
    global id
    lattime = time.time()
    if (lattime - curtime < 300 and id != 0):
        sql = "SELECT * FROM user where id = %s"
        value = (id,)
        mycursor.execute(sql, value)
        result = mycursor.fetchall()
        return render(request, "profile.html", {"username": result[0][1], "email": result[0][2]})
    else:
        id = 0
        return redirect('/')


def updatedetail(request):
    global id
    lattime = time.time()
    if (lattime - curtime < 300 and id != 0):
        username = request.POST['username']
        password = request.POST['pass']
        newpassword = request.POST['passnew']
        rnewpassword = request.POST['repassnew']
        email = request.POST['email']
        sql = "SELECT * FROM user where id = %s"
        value = (id,)
        mycursor.execute(sql, value)
        result = mycursor.fetchall()
        if (result[0][2] == hashlib.md5(password.encode()).hexdigest()):
            if (newpassword == rnewpassword and newpassword != ""):
                sql = "UPDATE `user` SET `username`=%s,`password`=%s,`email`=%s WHERE id = %s"
                value = (username, hashlib.md5(newpassword.encode()).hexdigest(), email, id)
                mycursor.execute(sql, value)
                mydb.commit()
                if (mycursor.rowcount != 1):
                    return render(request, "profile.html",
                                  {"username": result[0][1], "email": result[0][3], "message": "Cannot Update",
                                   "alert": "alert("})
            else:
                sql = "UPDATE `user` SET `username`=%s,`email`=%s WHERE id = %s"
                value = (username, email, id)
                mycursor.execute(sql, value)
                mydb.commit()
                if (mycursor.rowcount != 1):
                    return render(request, "profile.html",
                                  {"username": result[0][1], "email": result[0][3], "message": "Cannot Update",
                                   "alert": "alert("})
        else:
            return render(request, "profile.html",
                          {"username": result[0][1], "email": result[0][3], "message": "Wrong Password",
                           "alert": "alert("})
        sql = "SELECT * FROM user where id = %s"
        value = (id,)
        mycursor.execute(sql, value)
        result = mycursor.fetchall()
        return render(request, "profile.html",
                      {"username": result[0][1], "email": result[0][3], "message": "Update Successfully",
                       "alert": "alert("})
    else:
        id = 0
        return redirect('/')

def logout(request):
    global id
    id = 0
    return redirect('/')
