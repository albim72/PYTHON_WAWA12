from payement import Payement

class PayPallPayement(Payement):
    def __init__(self, amount, email):
        super().__init__(amount)
        self.email = email

    def pay(self):
        print(f"Płatność {self.get_amount()} , przyużyciu PayPall :{self.email}")
