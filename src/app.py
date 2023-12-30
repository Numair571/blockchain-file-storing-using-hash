from flask import Flask,render_template,request,redirect,session
from werkzeug.utils import secure_filename
import ipfsapi
import json
from web3 import Web3,HTTPProvider

def connect_with_register(wallet):
    blockchain="http://127.0.0.1:7545"
    web3=Web3(HTTPProvider(blockchain))
    print('Blockchain Server Connected')

    if wallet==0:
        web3.eth.defaultAccount=web3.eth.accounts[0]
    else:
        web3.eth.defaultAccount=wallet
    
    print('Wallet Selected')

    with open("../build/contracts/register.json") as f:
        artifact=json.load(f)
        abi=artifact['abi']
        address=artifact['networks']['5777']['address']
    
    contract=web3.eth.contract(abi=abi,address=address)
    print('Contract Selected')
    return contract,web3

def connect_with_file(wallet):
    blockchain="http://127.0.0.1:7545"
    web3=Web3(HTTPProvider(blockchain))
    print('Blockchain Server Connected')

    if wallet==0:
        web3.eth.defaultAccount=web3.eth.accounts[0]
    else:
        web3.eth.defaultAccount=wallet
    
    print('Wallet Selected')

    with open("../build/contracts/file.json") as f:
        artifact=json.load(f)
        abi=artifact['abi']
        address=artifact['networks']['5777']['address']
    
    contract=web3.eth.contract(abi=abi,address=address)
    print('Contract Selected')
    return contract,web3


app=Flask(__name__)
app.secret_key="madhu"
app.config['uploads']="uploads"

@app.route('/')
def homePage():
    return render_template('index.html')

@app.route('/login')
def loginPage():
    return render_template('login.html')

@app.route('/dashboard')
def dashboardPage():
    data=[]
    contract,web3=connect_with_file(0)
    _owners,_files=contract.functions.viewFiles().call()
    for i in range(len(_owners)):
        if _owners[i]==session['username']:
            dummy=[]
            dummy.append(_files[i])
            data.append(dummy)
    print(data)
    l=len(data)
    return render_template('dashboard.html',num=l,data=data)

@app.route('/logout')
def logoutPage():
    session['username']=None
    return redirect('/login')

@app.route('/indexdata',methods=['post'])
def indexdata():
    username=request.form['username']
    password=request.form['password']
    print(username,password)
    try:
        contract,web3=connect_with_register(0)
        tx_hash=contract.functions.signup(username,int(password)).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        return render_template('index.html',res='Account Success')
    except:
        return render_template('index.html',err="Already Exist")

@app.route('/logindata',methods=['post'])
def logindata():
    username=request.form['username1']
    password=request.form['password1']
    print(username,password)
    try:
        contract,web3=connect_with_register(0)
        status=contract.functions.login(username,int(password)).call()
        if(status==True):
            session['username']=username # session store 
            return redirect('/dashboard')
        else:
            return render_template('login.html',err="login failed")
    except:
        return render_template('login.html',err='dont have any account')

@app.route('/uploadfile',methods=['post'])
def uploadfile():
    chooseFile=request.files['chooseFile']
    doc=secure_filename(chooseFile.filename)
    chooseFile.save(app.config['uploads']+'/'+doc)
    client=ipfsapi.Client('127.0.0.1',5001)
    response=client.add(app.config['uploads']+'/'+doc)
    filehash=response['Hash']
    print(filehash)
    contract,web3=connect_with_file(0)
    tx_hash=contract.functions.uploadFile(session['username'],filehash).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/dashboard')

if __name__=="__main__":
    app.run(host='127.0.0.1',port=9000,debug=True)
