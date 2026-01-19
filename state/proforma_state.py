# state/proforma_state.py

from collections import defaultdict
from typing import List, Dict, Optional


class ProformaPhase:
    """
    Representa una fase lógica de la proforma:
    - IMPRIMACIÓN
    - CAPAS (1 CAPA, 2 CAPAS, 2 CAPAS VERDE, etc.)
    """

    def __init__(self, phase_type: str, title: str):
        self.phase_type: str = phase_type  # "IMPRIMACIÓN" | "CAPAS"
        self.title: str = title            # Texto del TITLE
        self.products: Dict[str, float] = defaultdict(float)
        # products[product_name] = total_kg

    def add_product(self, product_name: str, kg: float):
        if kg <= 0:
            return
        self.products[product_name] += kg


class ProformaState:
    """
    Estado completo de una proforma.
    Es la ÚNICA fuente de verdad.
    La UI solo renderiza lo que hay aquí.
    """

    def __init__(self):
        self.reset()

    # -------------------------
    # Estado base
    # -------------------------
    def reset(self):
        # Datos de cliente
        self.customer_name: Optional[str] = None
        self.customer_phone: Optional[str] = None

        # Fases (ordenadas)
        self.phases: List[ProformaPhase] = []

        # Herramientas
        self.include_tools: bool = True

    # -------------------------
    # Cliente
    # -------------------------
    def set_customer(self, name: Optional[str], phone: Optional[str]):
        self.customer_name = name
        self.customer_phone = phone

    # -------------------------
    # Fases
    # -------------------------
    def add_phase(self, phase_type: str, title: str) -> ProformaPhase:
        """
        Crea una fase nueva (no fusiona).
        La fusión se puede hacer externamente si se desea.
        """
        phase = ProformaPhase(phase_type, title)
        self.phases.append(phase)
        return phase

    def find_phase(self, phase_type: str, title: str) -> Optional[ProformaPhase]:
        """
        Devuelve una fase existente si coincide exactamente.
        Útil para 'Añadir productos'.
        """
        for phase in self.phases:
            if phase.phase_type == phase_type and phase.title == title:
                return phase
        return None

    def add_or_get_phase(self, phase_type: str, title: str) -> ProformaPhase:
        """
        Si existe una fase compatible, la reutiliza.
        Si no, crea una nueva.
        """
        phase = self.find_phase(phase_type, title)
        if phase:
            return phase
        return self.add_phase(phase_type, title)

    # -------------------------
    # Productos
    # -------------------------
    def add_product_to_phase(
        self,
        phase_type: str,
        title: str,
        product_name: str,
        kg: float
    ):
        """
        Añade producto acumulando kg.
        """
        phase = self.add_or_get_phase(phase_type, title)
        phase.add_product(product_name, kg)

    # -------------------------
    # Herramientas
    # -------------------------
    def enable_tools(self):
        self.include_tools = True

    def disable_tools(self):
        self.include_tools = False

    # -------------------------
    # Debug / utilidad
    # -------------------------
    def is_empty(self) -> bool:
        return len(self.phases) == 0

    def debug_dump(self):
        """
        Para debug rápido en consola.
        """
        print("=== PROFORMA STATE ===")
        print(f"Cliente: {self.customer_name} {self.customer_phone}")
        for phase in self.phases:
            print(f"[{phase.phase_type}] {phase.title}")
            for name, kg in phase.products.items():
                print(f"  - {name}: {kg:.2f} kg")
        print(f"Herramientas: {'Sí' if self.include_tools else 'No'}")
