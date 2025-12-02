import dis

class AI:
    def __init__(self,networks,name = "model_llm"):
        self.name=name
        self.networks=networks

class Osoba:
    def __new__(cls,imie,nazwisko=None,wiek=None,waga=None,wzrost=None):
        if imie == "model_llm":
            return super().__new__(AI)
        return super().__new__(Osoba)

    def __init__(self,imie,nazwisko=None,wiek=None,waga=None,wzrost=None):
        self.imie=imie
        self.nazwisko=nazwisko
        self.wiek=wiek
        self.waga=waga
        self.__wzrost=wzrost



    def get_waga(self):
        return self.waga

    def set_waga(self,nowawaga):
        self.waga=nowawaga

    @property
    def wzost(self):
        return self.__wzrost

    @wzost.setter
    def wzost(self, nowywzrost):
        self.__wzrost = nowywzrost

    @wzost.deleter
    def wzost(self):
        self.__wzrost = 1.7

    @property
    def wiek(self):
        return self._wiek

    @wiek.setter
    def wiek(self, nowywiek):
        self._wiek = nowywiek


os1 = Osoba("Jan","Kowalski",25,70,1.80)
print(f"waga: {os1.get_waga()}")
os1.set_waga(80)
print(f"waga: {os1.get_waga()}")

# os1.__wzrost = 1.90
# print(f"wzrost: {os1.__wzrost}")

os1.wzost = 1.90
print(f"wzrost: {os1.wzost}")
del os1.wzost
print(f"wzrost: {os1.wzost}")

print(f"wiek: {os1.wiek}")


print(dis.dis(Osoba) )

os2 = Osoba("model_llm")
print(type(os2))
