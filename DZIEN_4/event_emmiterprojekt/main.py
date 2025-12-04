from __future__ import annotations

from events import EventEmmiter
from order import Order
from services import NotificationService, AnalyticsService, InventoryService


def main() -> None:
    # 1.tworymy event bus
    event_bus = EventEmmiter(debug=True)

    # 2. Reejstracja komponentów
    notifications = NotificationService(event_bus)
    analytics = AnalyticsService(event_bus)
    inventory = InventoryService(event_bus)

    #3. listener jednorazzowy
    def audit_first_order(order_id:int, amount:float) -> None:
        print(f"[AUDIT] pierwsze zwmówienie w systemie: #{order_id}, kwota: {amount:.2f} PLN")

    event_bus.once("order_placed",audit_first_order)

    #komponent domenowy
    order_component = Order(event_bus)
    
    #symulujemy kilka zamówień
    orders = [
        (101,299.99),
        (102,67.88),
        (103,2100.00),
        (104,1233.90),
        (105,987.23),
    ]

    for order_id,amount in orders:
        order_component.place_order(order_id,amount)

    print("==== koniec symulacji =====")
    print(f"łączenie zamówień: {analytics.orders_count}")
    print(f"łaczny obrót: {analytics.total_revenue:.2f} PLN")

if __name__ == '__main__':
    main()
