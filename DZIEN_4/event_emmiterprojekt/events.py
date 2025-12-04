from __future__ import annotations

from collections import defaultdict
from typing import Callable, Any, DefaultDict

#Alias  typu dla czytelności - każdy Listener to funckja przyjmująca dowolne argumenty
Listener = Callable[..., None]

class EventEmmiter:
    """
    Prpsty event bus:
     - on - rejestracja słuchacza
     - off - usunięcie słuchacza
     - once - jednorazowe wywołamnie
     - emit - publikacja zdarzenia
    """
 
    
    def __init__(self,debug:bool = True) -> None:
        self._listeners: DefaultDict[str, list[Listener]] = defaultdict(list)
        self._debug = debug
        
    def on(self,event:str,listener:Listener)->None:
        self._listeners[event].append(listener)
        if self._debug:
            print(f"[DRBUG] Listener: {listener} added for event {event}")
            
    def off(self,event:str,listener:Listener)->None:
        """usunięcie słuchacza"""
        if event in self._listeners:
            return 
        try:
            self._listeners[event].remove(listener)
            if self._debug:
                print(f"[DRBUG] Listener: {listener} removed for event {event}")    
        except ValueError:
            pass
        
    def once(self,event:str,listener: Listener)->None:
        """Rejestracja listenera jednorazowego"""
        
        def _wrapper(*args:Any, **kwargs:Any)->None:
            self.off(event,_wrapper)
            if self._debug:
                print(f"[DRBUG] Listener: {listener} called for event {event}")
            listener(*args,**kwargs)
            
        self.on(event,_wrapper)
        
    def emit(self,event:str,*args:Any,**kwargs:Any)->None:
        """Publikacja zdarzenia"""
        if self._debug:
            print(f"[DRBUG] Event: {event} emitted with args: {args} and kwargs: {kwargs}")
        
        for listener in list(self._listeners.get(event,[])):
            listener(*args,**kwargs)
        
        
        
    
