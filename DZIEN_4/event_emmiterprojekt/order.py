from __future__ import annotations

from events import EventEmmiter

class Order:
    """Komponent domenowy odpowiedzialny za skaldanie zamówień"""
    def __init__(self,event_emitter:EventEmmiter) -> None:
        self.event_emitter = event_emitter

    def place_order(self,order_id:int,amount:float)->None:
        print(f"[ORDER] złożono zamówienie #{order_id}, kwota: {amount:.2f} PLN")
        self.event_emitter.emit("order_placed",order_id,amount=amount)
        
        if amount > 5000:
            self.event_emitter.emit("order_placed_high_value",order_id,amount=amount)
