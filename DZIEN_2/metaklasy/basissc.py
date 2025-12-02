class MojaMeta(type):
    def __new__(cls, name, bases, attrs):
        print(f"______________ {cls.__class__.__name__} _________________")
        print(f"nazwa klasy: {name}")
        print(f"klasy dziedziczone: {bases}")
        print(f"atrybuty klasy: {attrs}")
        return type.__new__(cls, name, bases, attrs)

    def jedynka(cls):
        return 1

class S:
    pass

class F:
    pass

class Specjalna(metaclass=MojaMeta):
    pass

class B(Specjalna):
    pass

class C(F,B):
    @property
    def info(self):
        print("abc...")

class D(F):
    pass

obiekt_c = C()
# print(obiekt_c.jedynka())

klasa_c = C
print(klasa_c.jedynka())
