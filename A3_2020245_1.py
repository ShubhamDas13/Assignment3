from flask import Flask,render_template,request
import pandas as pd
from glob import glob
from datetime import timedelta, datetime


app = Flask(__name__)

data_names = glob("archive/*")
df = pd.DataFrame(data_names)
data_fileloc = dict(df)
Names = []
FileLoc = []

def giveData(fileloc):
    csvfile = pd.read_csv(fileloc)
    data_file = pd.DataFrame(csvfile)
    return data_file

def giveName(fileloc):
    a = fileloc
    n = a.replace("archive",'')
    name = n[1:len(n)-4]
    return name

for i in range(len(data_fileloc[0])):
    path_file = data_fileloc[0][i]
    FileLoc.append(path_file)
    Names.append(giveName(path_file))

def creategrplist(name,start,end,T):
    lst = []
    loc = FileLoc[Names.index(name)]
    data = giveData(loc)
    if T==1:
        group = data['High'].groupby(data['Date'])
    elif T==0:
        group = data['Low'].groupby(data['Date'])
    l = list(group)
    for i in l:
        if datetime.strptime(i[0],'%Y-%m-%d').date() >start and datetime.strptime(i[0],'%Y-%m-%d').date()<end:
            lst.append(float(i[1]))
    return lst


def gethigh(name,start,end):
    highlist = creategrplist(name,start,end,1)
    if len(highlist)==0:
        return highlist
    high = max(highlist)
    return high


def getlow(name,start,end):
    lowlist = creategrplist(name,start,end,0)
    if len(lowlist)==0:
        return lowlist
    low = min(lowlist)
    return low

def wrongFormat(start,end):
    if start>end:
        return True
    
def givestart(name):
    lst=[]
    loc = FileLoc[Names.index(name)]
    data = giveData(loc)
    group = data['High'].groupby(data['Date'])
    l = list(group)
    for i in l:
        lst.append(i[0])
    date = min(lst)
    return date


@app.route('/')
def index():
    return render_template('Index.html', nameslist=Names)

@app.route('/submit', methods = ['POST','GET'])
def submit():
    if request.method == 'POST':
        comp = request.form["namelist"]
        start = request.form["Start_Date"]
        end = request.form["End_Date"]
        if comp=="Select Company":
            return render_template('name.html', nameslist=Names)
        if start=="" and end=="":
            return render_template('nodates.html', nameslist=Names)
        if start == "" and end != "":
            a =datetime.strptime(end,'%Y-%m-%d').date()
            start = a-timedelta(days=52)
            check = gethigh(comp,start,a)
            if check == []:
                start = datetime.strptime(givestart(comp),'%Y-%m-%d').date()
        else:
            start = datetime.strptime(start,'%Y-%m-%d').date()
        if end == "":
            end = start+timedelta(days=52)
        else:
            end = datetime.strptime(end,'%Y-%m-%d').date()
        if wrongFormat(start,end):
            return render_template('wrong.html', nameslist=Names)
        high = gethigh(comp,start,end)
        low = getlow(comp,start,end)
        if high == [] or low == []:
            return render_template('nodata.html', nameslist=Names)
    return render_template("data.html",comp=comp,nameslist=Names,start=start,end=end,high=high,low=low)

if __name__=="__main__":
    app.run(debug=True)