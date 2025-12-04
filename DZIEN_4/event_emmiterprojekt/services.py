from __future__ import annotations

from events import EventEmmiter

class NotificationService:
    """Serwis  odpowiedzialny za powiadomienia o nowych zamówieniach"""

    def __init__(self,event_emitter:EventEmmiter) -> None:
        event_emitter.on("order_placed",self.senf_notification)

    def senf_notification(self,order_id:int,amount:float)->None:
        print(f'[NOTIFICATION] wysłano powiadomienie o zamówieniu #{order_id}, kwota: {amount:.2f} PLN')

class AnalyticsService:
    """Serwis analityczny - zlicza liczbę zamówień i sumaryczny obrót"""

    def __init__(self,event_emitter:EventEmmiter) -> None:
        self.total_revenue = 0.0
        self.orders_count = 0
        event_emitter.on("order_placed",self._on_order_placed)
    def _on_order_placed(self,order_id:int,amount:float)->None:
        self.orders_count += 1
        self.total_revenue += amount
        print(
            f"[ANALYTICS] zarejestrowno zamówienie #{order_id} |"
            f"liczba zmówień: {self.orders_count} |"
            f"łączny obrót: {self.total_revenue:.2f} PLN"
        )

class InventoryService:
    """serwis magazynowy - symulacja rezerwacji towaru"""
    def __init__(self,event_emitter: EventEmmiter) -> None:
        event_emitter.on("order_placed",self.reserve_stock)

    def reserve_stock(self,order_id:int,amount:float)->None:
        print(f"[INVENTORY] zarezerwowano towar dla zamówienia #{order_id} (symulacja)")
