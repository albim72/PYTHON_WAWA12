"""
Mocny przykład SQLAlchemy + SQLite
----------------------------------

Pokazuje:
- deklaratywne modele ORM (SQLAlchemy 2.0, typed ORM)
- relacje One-To-Many (Customer -> Order, Order -> OrderItem)
- relację Many-To-One (OrderItem -> Product)
- unikalne ograniczenia i indeksy
- hybrid_property + expression (Order.total_amount)
- kontekstowe sesje i transakcje
- złożone zapytania z agregacją, podzapytaniami i eager loadingiem
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Numeric,
    ForeignKey,
    DateTime,
    func,
    select,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    Session,
    selectinload,
)
from sqlalchemy.ext.hybrid import hybrid_property


# === Konfiguracja bazy ===

# Dla demo: plik lokalny. Na szkoleniu można pokazać też :memory:
engine = create_engine("sqlite:///shop.db", echo=False, future=True)


class Base(DeclarativeBase):
    """Bazowa klasa dla wszystkich modeli."""
    pass


# === MODELE ===

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    # relacja: Customer -> Order (One-To-Many)
    orders: Mapped[list[Order]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Customer id={self.id} email={self.email!r}>"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # relacja wsteczna: Product -> OrderItem (One-To-Many)
    items: Mapped[list[OrderItem]] = relationship(back_populates="product")

    def __repr__(self) -> str:
        return f"<Product sku={self.sku!r} price={self.price}>"


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_created_status", "created_at", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="NEW", index=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )

    customer: Mapped[Customer] = relationship(back_populates="orders")

    # relacja Order -> OrderItem (One-To-Many)
    items: Mapped[list[OrderItem]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @hybrid_property
    def total_amount(self) -> Decimal:
        """Suma wartości zamówienia po stronie Pythona."""
        return sum((item.quantity * item.unit_price for item in self.items), start=Decimal("0.00"))

    @total_amount.expression
    def total_amount(cls):
        """
        Ta sama logika po stronie SQL – pozwala używać Order.total_amount
        w filtrach, ORDER BY, HAVING itd.
        """
        from sqlalchemy import select, literal_column

        return (
            select(func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0))
            .where(OrderItem.order_id == cls.id)
            .correlate(cls)
            .scalar_subquery()
        )

    def __repr__(self) -> str:
        return f"<Order id={self.id} status={self.status!r}>"


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        UniqueConstraint("order_id", "product_id", name="uq_order_product"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped[Order] = relationship(back_populates="items")
    product: Mapped[Product] = relationship(back_populates="items")

    def __repr__(self) -> str:
        return (
            f"<OrderItem order_id={self.order_id} "
            f"product_id={self.product_id} qty={self.quantity}>"
        )


# === Funkcje pomocnicze ===

def recreate_schema() -> None:
    """Czyści i tworzy schemat bazy."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def seed_data(session: Session) -> None:
    """Zasiew danych demo."""
    # Produkty
    p1 = Product(sku="LAPTOP-ULTRA", name="Laptop Ultra 15", price=Decimal("6999.99"))
    p2 = Product(sku="MONITOR-4K", name="Monitor 4K 27", price=Decimal("1999.50"))
    p3 = Product(sku="MOUSE-PRO", name="Mysz Pro", price=Decimal("249.99"))

    # Klienci
    c1 = Customer(email="alice@example.com", name="Alice")
    c2 = Customer(email="bob@example.com", name="Bob")
    c3 = Customer(email="carol@example.com", name="Carol")

    session.add_all([p1, p2, p3, c1, c2, c3])
    session.flush()  # mamy już id w pamięci

    # Zamówienia (pokazujemy, jak działa cascade na items)
    o1 = Order(customer=c1, status="PAID")
    o1.items = [
        OrderItem(product=p1, quantity=1, unit_price=p1.price),
        OrderItem(product=p3, quantity=2, unit_price=p3.price),
    ]

    o2 = Order(customer=c1, status="PAID")
    o2.items = [
        OrderItem(product=p2, quantity=2, unit_price=p2.price),
    ]

    o3 = Order(customer=c2, status="NEW")
    o3.items = [
        OrderItem(product=p3, quantity=5, unit_price=p3.price),
    ]

    session.add_all([o1, o2, o3])
    session.commit()


# === Przykładowe zapytania ===

def show_customers_with_totals(session: Session) -> None:
    """
    Przykład użycia hybrid_property w zapytaniu:
    - top klienci wg sumy zamówień
    """
    stmt = (
        select(
            Customer.name,
            Customer.email,
            func.coalesce(func.sum(Order.total_amount), 0).label("total_spent"),
        )
        .join(Customer.orders, isouter=True)
        .group_by(Customer.id)
        .order_by(func.sum(Order.total_amount).desc())
    )

    print("\n== TOP klienci wg wydanych pieniędzy ==")
    for row in session.execute(stmt):
        print(f"{row.name:>6} ({row.email}) -> {row.total_spent} PLN")


def show_large_orders(session: Session, threshold: Decimal) -> None:
    """
    Zamówienia powyżej progu kwotowego – filtr po stronie SQL na Order.total_amount.
    """
    stmt = (
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .where(Order.total_amount >= threshold)
        .order_by(Order.total_amount.desc())
    )

    print(f"\n== Zamówienia >= {threshold} PLN ==")
    for order in session.scalars(stmt):
        print(f"Order {order.id} ({order.status}) total={order.total_amount} PLN")
        for item in order.items:
            print(
                f"   - {item.product.name:15} x{item.quantity} "
                f"@ {item.unit_price} = {item.quantity * item.unit_price}"
            )


def show_hot_products(session: Session) -> None:
    """
    Produkty posortowane wg liczby sprzedanych sztuk (agregacja po OrderItem).
    """
    stmt = (
        select(
            Product.name,
            func.coalesce(func.sum(OrderItem.quantity), 0).label("qty_sold"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id, isouter=True)
        .group_by(Product.id)
        .order_by(func.sum(OrderItem.quantity).desc())
    )

    print("\n== Najczęściej kupowane produkty ==")
    for row in session.execute(stmt):
        print(f"{row.name:15} -> {row.qty_sold} szt.")


def demonstrate_transaction_rollback(session: Session) -> None:
    """
    Pokażemy transakcję, która się wycofa (rollback),
    oraz to, że dane nie trafią do bazy.
    """
    print("\n== Demonstracja transakcji z rollbackiem ==")
    print("Liczba klientów przed:", session.scalar(select(func.count(Customer.id))))

    try:
        with session.begin():
            tmp = Customer(email="temp@example.com", name="Temporary")
            session.add(tmp)
            # Symulujemy fatalny błąd domenowy / walidację
            raise ValueError("Ups, biznes nie pozwala na tego klienta.")
    except ValueError as exc:
        print("Transakcja wycofana z powodu:", exc)

    print("Liczba klientów po:", session.scalar(select(func.count(Customer.id))))


def main() -> None:
    recreate_schema()

    # Sesja główna – dla demo można wszystko w jednej
    with Session(engine) as session:
        seed_data(session)

    # Nowa sesja do dalszych operacji
    with Session(engine) as session:
        show_customers_with_totals(session)
        show_large_orders(session, threshold=Decimal("3000.00"))
        show_hot_products(session)
        demonstrate_transaction_rollback(session)


if __name__ == "__main__":
    main()
