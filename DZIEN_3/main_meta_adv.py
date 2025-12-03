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
