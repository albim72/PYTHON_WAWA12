from advanced_metaclasses import *

if __name__ == '__main__':
    print("\n==== 1) RegistryMeta - automatyczna rejestracja klas ====\n")
    class ServiceA(BaseRegistry):
        pass

    class ServiceB(BaseRegistry):
        pass

    print(f"Registry zawiera: {registry}")

    print("\n==== 2) RequireMethodMeta - wymuszenie metody run() ====\n")

    class Job(BaseRequire):
        def run(self):
            print("Uruchomiony Job")

    job = Job()
    job.run()


    # class JobTest(BaseRequire):
    #     def runs(self):
    #         print("Uruchomiony JobTest - nie ma metody run()")
    #
    #
    # jobt = JobTest()
    # jobt.runs()
    print("\n==== 3) Autologowanie wszystkich metod ====\n")
    class Worker(metaclass=AutoLoggedMeta):
        def process(self, x):
            print(f"wynik = {x*3}")
        def ekstra(self,info):
            print(f"dodatkowe informacje: {info}")
        def wybor(self,x):
            print(f"wybrany element parzysty: {x%2==0}")

    w = Worker()
    w.process(5)
    w.ekstra("informacje dodatkowe")
    w.wybor(10)

    print("\n==== 4) Generowanie __init__ z adnotacji ====\n")
    class Point(metaclass=AutoInitMeta):
        x:int
        y:int
        label:str

    p1 = Point(4,7,"p1")
    p2 = Point(11,1,"p2")

    print(f"Point p1: {p1.__dict__}")
    print(f"Point p2: {p2.__dict__}")

    print("\n==== 5) Singleton ====\n")
    class Config(metaclass=SingletonMeta):
        def __init__(self):
            print("Config zainicjowany")
            self.value = 42
    c1 = Config()
    c2 = Config()
    print(f"c1 == c2: {c1 == c2}")
    print(f"c1.value: {c1.value}")
    print(f"c2.value: {c2.value}")
    print(f"c1 is c2: {c1 is c2}")
    print(f"c1.id: {id(c1)} - c2.id: {id(c2)}")

