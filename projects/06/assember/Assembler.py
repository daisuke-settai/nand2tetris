import Code
import Parser
import SymbolTable
import sys
import re
import logging

def assemble():
    logging.debug(sys.argv)
    if (len(sys.argv) != 2) or (not sys.argv[1].endswith(".asm")):
        raise Exception("Usage: {} src_file".format(__file__))
    parser = Parser.Parser(sys.argv[1])
    code = Code.Code()
    symbol_table = SymbolTable.SymbolTable()
    dst_file = open(re.sub("\.asm$", ".hack", sys.argv[1]), "w")

    # 1st Path
    ## L_Symbol
    PC = 0
    while parser.advance():
        cmd_type = parser.commandType()
        if cmd_type is parser.A_COMMAND:
            PC += 1
        elif cmd_type is parser.L_COMMAND:
            symbol = parser.symbol()
            if not symbol_table.contains(symbol):
                symbol_table.addEntry(symbol, PC)
            else:
                raise Exception("Error: Dual Definition of l_symbol: {}".format(symbol))
        elif cmd_type is parser.C_COMMAND:
            PC += 1
        else:
            raise Exception("Error")

    parser = Parser.Parser(sys.argv[1])
    # 2nd Path
    while parser.advance():
        cmd_type = parser.commandType()
        logging.debug("cmd_type: {}".format(cmd_type))
        if cmd_type is parser.A_COMMAND:
            symbol = parser.symbol()
            try:
                const_num = int(symbol)
                ostr = "{:016b}\n".format(const_num)
                logging.debug("output: {}".format(ostr))
                dst_file.write(ostr)
            except ValueError:
                if symbol_table.contains(symbol):
                    address = symbol_table.getAddress(symbol)
                    ostr = "{:016b}\n".format(address)
                    dst_file.write(ostr)
                else:
                    # new local varialble
                    address = symbol_table.addLocalVar(symbol)
                    ostr = "{:016b}\n".format(address)
                    dst_file.write(ostr)
        elif cmd_type is parser.L_COMMAND:
            pass
        elif cmd_type is parser.C_COMMAND:
            dest = parser.dest()
            comp = parser.comp()
            jump = parser.jump()
            logging.debug("dest: {}, comp: {}, jump: {}".format(dest, comp, jump))
            ostr = "111{comp}{dest}{jump}\n".format( \
                comp=code.comp(comp), dest=code.dest(dest), jump=code.jump(jump))
            logging.debug("output: {}".format(ostr))
            dst_file.write(ostr)
        else:
            raise Exception("Error")
    
    dst_file.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    assemble()