from payement import Payement

class CryptoPayement(Payement):
    def __init__(self, amount, wallet_address):
        super().__init__(amount)
        self.wallet_address = wallet_address

    def pay(self):
        print(f"Płatność {self.get_amount()} , przyużyciu portfela crypto :{self.wallet_address}")
