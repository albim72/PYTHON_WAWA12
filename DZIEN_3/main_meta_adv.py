from advanced_metaclasses import *

if __name__ == '__main__':
    print("\n==== 1) RegistryMeta - automatyczna rejestracja klas ====\n")
    class ServiceA(BaseRegistry):
        pass

    class ServiceB(BaseRegistry):
        pass

    print(f"Registry zawiera: {registry}")
