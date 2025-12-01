def show_info(*args, **kwargs):

    print(f"lista argumentów: {args}")
    print(f"słownik arguemntów: {kwargs}")

show_info(1, 2, 3, a=4, b=5)
show_info("fff",True,75,8.8 ,ln = 88, j = "lolek", nn= False)


def create_order(client_name,*dishes,**extras):
    print(f"Zamówienie dla - Klient: {client_name}")

    if dishes:
        print("Zamówienie dnia...")
        for dish in dishes:
            print(f"- {dish}")
    else:
            print("brak zamówionych dan")

    if extras:
        print("\nDodatkowe opcje:")
        for key,value in extras.items():
            print(f"- {key.replace('_',' ').title()}: {value}")
    else:
        print("\nBrak dodatkowych opcji")
    print("Zamówenie zostało przyjęte....")

create_order("Anna","Pzza Margarita","Lasagne",napoj = "cola", sos="czosnkowy")
create_order("Tomek",napoj = "fanta", uwagi="bez glutenu",pieczywo_dnia = "bułka żytnia")
create_order("Ola","Frytki","Sałatka")
