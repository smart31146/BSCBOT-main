import time
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
import threading
from web3 import Web3
import datetime
import json
import asyncio
import requests
import os
import sys
import ctypes
import random


os.system("mode con: lines=32766")
os.system("")  # allows different colour text to be used


class style():  # Class of different text colours - default is white
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


print(style.MAGENTA)  # change following text to magenta

currentTimeStamp = ""
run=False


def getTimestamp():
        timeStampData = datetime.datetime.now()
        global currentTimeStamp
        currentTimeStamp = "[" + \
            timeStampData.strftime("%H:%M:%S.%f")[:-3] + "]"




numTokensDetected = 0
numTokensBought = 0
walletBalance = 0

bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))

if web3.isConnected():
    print(currentTimeStamp + " [Info] Web3 successfully connected")

# load json data

configFilePath = os.path.abspath('') + '\config.json'

with open(configFilePath, 'r') as configdata:
    data = configdata.read()

# parse file
obj = json.loads(data)

# load config data from JSON file into program
pancakeSwapRouterAddress = obj['pancakeSwapRouterAddress']
# read from JSON later
pancakeSwapFactoryAddress = '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73'
walletAddress = obj['walletAddress']
# private key is kept safe and only used in the program
private_key = obj['walletPrivateKey']
# number of seconds after transaction processes to cancel it if it hasn't completed
transactionRevertTime = int(obj['transactionRevertTimeSeconds'])
gasAmount = int(obj['gasAmount'])
gasPrice = int(obj['gasPrice'])
bscScanAPIKey = obj['bscScanAPIKey']
observeOnly = obj['observeOnly']

checkSourceCode = obj['checkSourceCode']
checkValidPancakeV2 = obj['checkValidPancakeV2']
checkMintFunction = obj['checkMintFunction']
checkHoneypot = obj['checkHoneypot']
checkPancakeV1Router = obj['checkPancakeV1Router']

enableMiniAudit = False

if checkSourceCode == "True" and (checkValidPancakeV2 == "True" or checkMintFunction == "True" or checkHoneypot == "True" or checkPancakeV1Router == "True"):
    enableMiniAudit = True


def updateTitle():
    # There are references to ether in the code but it's set to BNB, its just how Web3 was originally designed
    walletBalance = web3.fromWei(web3.eth.get_balance(walletAddress), 'ether')
    # the number '4' is the wallet balance significant figures + 1, so shows 5 sig figs
    walletBalance = round(
        walletBalance, -(int("{:e}".format(walletBalance).split('e')[1]) - 4))
    print("BSCTokenSniper | Tokens Detected: " + str(
        numTokensDetected) + " | Tokens Bought: " + str(numTokensBought) + " | Wallet Balance: " + str(walletBalance) + " BNB")

getTimestamp()
updateTitle()


print(currentTimeStamp + " [Info] Using Wallet Address: " + walletAddress)


pancakeABI = '[{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'
listeningABI = json.loads('[{"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token0","type":"address"},{"indexed":true,"internalType":"address","name":"token1","type":"address"},{"indexed":false,"internalType":"address","name":"pair","type":"address"},{"indexed":false,"internalType":"uint256","name":"","type":"uint256"}],"name":"PairCreated","type":"event"},{"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"createPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"feeTo","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"feeToSetter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeTo","type":"address"}],"name":"setFeeTo","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"name":"setFeeToSetter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]')
tokenNameABI = json.loads('[ { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "owner", "type": "address" }, { "indexed": true, "internalType": "address", "name": "spender", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "value", "type": "uint256" } ], "name": "Approval", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "from", "type": "address" }, { "indexed": true, "internalType": "address", "name": "to", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "value", "type": "uint256" } ], "name": "Transfer", "type": "event" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "_owner", "type": "address" }, { "internalType": "address", "name": "spender", "type": "address" } ], "name": "allowance", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address", "name": "spender", "type": "address" }, { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "approve", "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": true, "inputs": [ { "internalType": "address", "name": "account", "type": "address" } ], "name": "balanceOf", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "decimals", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "getOwner", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "name", "outputs": [ { "internalType": "string", "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "symbol", "outputs": [ { "internalType": "string", "name": "", "type": "string" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": true, "inputs": [], "name": "totalSupply", "outputs": [ { "internalType": "uint256", "name": "", "type": "uint256" } ], "payable": false, "stateMutability": "view", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address", "name": "recipient", "type": "address" }, { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "transfer", "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address", "name": "sender", "type": "address" }, { "internalType": "address", "name": "recipient", "type": "address" }, { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "transferFrom", "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ], "payable": false, "stateMutability": "nonpayable", "type": "function" } ]')


root = tk.Tk(className='bsc_Bot')
root.geometry("750x550")


class My_App(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        lblTitile = Label(self.parent, font="Verdana 15 bold",
                          text="BSC Black BOX")
        lblTitile.place(x=350, y=40)

        self.lblAddress = Label(self.parent, font="Verdana 10 bold")
        self.lblAddress.place(x=50, y=90)
        self.lblAddress.config(text="CONTRACT ADDRESS")

        self.txtAddress = Text(self.parent, height=1, width=40)
        self.txtAddress.place(x=260, y=90)

        self.lblBalance = Label(self.parent, font="Verdana 10 bold")
        self.lblBalance.place(x=50, y=130)
        self.lblBalance.config(text="WALLET BALANCE(BNB)")

        self.txtBalance = Text(self.parent, height=1, width=40)
        self.txtBalance.place(x=260, y=130)

    # Trading Info

        lblInfo = Label(self.parent, font="Verdana 15 bold", text="TRADE INFO")
        lblInfo.place(x=350, y=180)

        self.lblMinimum = Label(self.parent, font="Verdana 10 bold")
        self.lblMinimum.place(x=280, y=210)
        self.lblMinimum.config(text="MINIMUM BUY")

        self.txtMinimum = Text(self.parent, height=1, width=20)
        self.txtMinimum.place(x=400, y=210)

        self.lblMaximum = Label(self.parent, font="Verdana 10 bold")
        self.lblMaximum.place(x=280, y=240)
        self.lblMaximum.config(text="MAXIMUM BUY")

        self.txtMaximum = Text(self.parent, height=1, width=20)
        self.txtMaximum.place(x=400, y=240)

    # Time Interval Setting

        lblEvery = Label(self.parent, font="Verdana 15 bold")
        lblEvery.place(x=350, y=270)
        lblEvery.config(text="BUY EVERY")

        self.txtMinTime = Text(self.parent, height=1, width=10)
        self.txtMinTime.place(x=320, y=300)

        self.lblTemp = Label(self.parent, font="Verdana 10 bold")
        self.lblTemp.place(x=400, y=300)
        self.lblTemp.config(text="--")

        self.txtMaxTime = Text(self.parent, height=1, width=10)
        self.txtMaxTime.place(x=420, y=300)

    # Stop/Start Button

        self.btnStart = tk.Button(
            self.parent, font="Verdana 15 bold", text="STOP/START", command=self.Start, width=12)
        self.btnStart.pack()
        self.btnStart.place(x=350, y=350)

        self.lblMark = Label(self.parent, font="Verdana 8 bold")
        self.lblMark.place(x=400, y=400)
        self.lblMark.config(text="imvi works")
        self.updateBalance()

    def Start(self):
        global run
        if run:
            run=False
        else:
            run=True 
            self.Buy()
    def updateBalance(self):
        # There are references to ether in the code but it's set to BNB, its just how Web3 was originally designed
        walletBalanceNow = web3.fromWei(web3.eth.get_balance(walletAddress), 'ether')
        # the number '4' is the wallet balance significant figures + 1, so shows 5 sig figs
        walletBalanceNow = round(
            walletBalanceNow, -(int("{:e}".format(walletBalanceNow).split('e')[1]) - 4))
        self.txtBalance.delete("1.0", END)
        self.txtBalance.insert(END,str(walletBalanceNow))



    def Buy(self):
        global run
        if run:
            minTime = self.txtMinTime.get("1.0", "end-1c")
            maxTime = self.txtMaxTime.get("1.0", "end-1c")
            intervalTime=random.randint(int(minTime), int(maxTime))
            print("=====TimeInterveral:==   "+str(intervalTime))
            tokenAddress = self.txtAddress.get("1.0", "end-1c")
            minBuyAmt = self.txtMinimum.get("1.0", "end-1c")
            maxBuyAmt = self.txtMaximum.get("1.0", "end-1c")
            snipeBNBAmount=round(random.uniform(float(minBuyAmt), float(maxBuyAmt)), 5)
            print("BuyBNBAmount==="+str(snipeBNBAmount))
            if(tokenAddress != None):
                tokenToBuy = web3.toChecksumAddress(tokenAddress)
                spend = web3.toChecksumAddress(
                    "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")  # wbnb contract address,0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73
                contract = web3.eth.contract(
                    address=pancakeSwapRouterAddress, abi=pancakeABI)
                nonce = web3.eth.get_transaction_count(walletAddress)
                start = time.time()
                pancakeswap2_txn = contract.functions.swapExactETHForTokens(
                    0,  # Set to 0 or specify min number of tokens - setting to 0 just buys X amount of token at its current price for whatever BNB specified
                    [spend, tokenToBuy],
                    walletAddress,
                    (int(time.time()) + transactionRevertTime)
                ).buildTransaction({
                    'from': walletAddress,
                    # This is the Token(BNB) amount you want to Swap from
                    'value': web3.toWei(float(snipeBNBAmount), 'ether'),
                    'gas': gasAmount,
                    'gasPrice': web3.toWei(gasPrice, 'gwei'),
                    'nonce': nonce,
                })

                try:
                    signed_txn = web3.eth.account.sign_transaction(
                        pancakeswap2_txn, private_key)
                    tx_token = web3.eth.send_raw_transaction(
                        signed_txn.rawTransaction)  # BUY THE TOKEN
                except:
                    print(style.RED + currentTimeStamp + " Transaction failed.")
                    print("")  # line break: move onto scanning for next token

                txHash = str(web3.toHex(tx_token))

                # TOKEN IS BOUGHT

                checkTransactionSuccessURL = "https://api.bscscan.com/api?module=transaction&action=gettxreceiptstatus&txhash=" + \
                    txHash + "&apikey=" + bscScanAPIKey
                checkTransactionRequest = requests.get(
                    url=checkTransactionSuccessURL)
                txResult = checkTransactionRequest.json()['status']

                if(txResult == "1"):
                    print(style.GREEN + currentTimeStamp + " Successfully bought $TOKEN for " +
                        style.BLUE + str(snipeBNBAmount) + style.GREEN + " BNB - TX ID: ", txHash)

                else:
                    print(style.RED + currentTimeStamp +
                        " Transaction failed: likely not enough gas.")

                getTimestamp()
                updateTitle()
                self.updateBalance()
                time.sleep(intervalTime)
                self.Buy()
        else:
            print("=======Please insert Tokenaddress=======")


root.resizable(False, False)
My_App(root)
root.mainloop()
