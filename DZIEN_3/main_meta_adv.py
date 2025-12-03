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
