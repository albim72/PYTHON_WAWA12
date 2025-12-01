from creditcard import CreditCard
from  paypall import PayPallPayement
from crypto import CryptoPayement
from payement import Payement

def process_payement(payement: Payement):
    payement.pay()

payments = [
        CreditCard(780,"75664556565"),
        PayPallPayement(100,"mmm@fdsf.pl"),
        CryptoPayement(4356,"$$#FSDFDSDSDSDSDFSDFFSDF$3434")


    ]

for p in payments:
    process_payement(p)
