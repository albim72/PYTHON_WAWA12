from abc import ABC,abstractmethod

class Payement(ABC):
    def __init__(self,amount):
        self._amount=amount#enkapsulacja - prywatny argument
        
    # def __new__(cls, *args, **kwargs):
    #     return super().__new__(Payement) 
    @abstractmethod
    def pay(self):
        pass
    
    def get_amount(self):
        return self._amount
    
    def set_amount(self,newamount):
        self._amount=newamount
