from payement import Payement

class CreditCard(Payement):
    def __init__(self, amount, card_number):
        super().__init__(amount)
        self.card_number = card_number

    def pay(self):
        print(f"Płatność {self.get_amount()} zl z uzenim karty {self.card_number}")
