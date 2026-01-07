from dataclasses import dataclass, field

@dataclass
class ProformaRow:
    type: str

    col_0: str = ""
    col_1: str = ""
    col_2: str = ""
    col_3: str = ""
    col_4: str = ""

    def as_list(self):
        return [
            self.col_0,
            self.col_1,
            self.col_2,
            self.col_3,
            self.col_4,
        ]
