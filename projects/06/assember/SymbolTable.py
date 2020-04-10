import logging

class SymbolTable():
    defined_symbols = {
        "SP":         0,
        "LCL":        1,
        "ARG":        2,
        "THIS":       3,
        "THAT":       4,
        "R0":         0,
        "R1":         1,
        "R2":         2,
        "R3":         3,
        "R4":         4,
        "R5":         5,
        "R6":         6,
        "R7":         7,
        "R8":         8,
        "R9":         9,
        "R10":       10,
        "R11":       11,
        "R12":       12,
        "R13":       13,
        "R14":       14,
        "R15":       15,
        "SCREEN": 16384,
        "KBD":    24576,
    }

    def __init__(self):
        self.table = self.defined_symbols
        self.local_var_address = 16

    def addEntry(self, symbol: str, address: int) -> None:
        """
        デーブルに(symbol, address)のペアを追加
        """
        if not self.contains(symbol):
            logging.debug("SybmolTable: Add {} => {}".format(symbol, address))
            self.table[symbol] = address

    def contains(self, symbol: str) -> bool:
        """
        テーブルにsymbolを含むか？
        """
        return symbol in self.table.keys()

    def getAddress(self, symbol: str) -> int:
        """
        symbolに結び付けられたアドレスを返す
        """
        address = self.table.get(symbol) 
        return address if address != None else -1

    def addLocalVar(self, symbol: str) -> int:
        """
        symbolを登録
        """
        if not self.contains(symbol):
            self.addEntry(symbol, self.local_var_address)
            self.local_var_address += 1
        return self.getAddress(symbol)