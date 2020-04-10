import re
import logging

class Parser():
    A_COMMAND = 1
    C_COMMAND = 2
    L_COMMAND = 3

    A_COMMAND_REGREP_SYMBOL = re.compile("^@[a-zA-Z][\w\.\$:]*$")
    A_COMMAND_REGREP_NUM = re.compile("^@[\d]+$")
    C_COMMAND_REGREP = re.compile("(?:(A?M?D?)=)?([^;]+)(?:;(.+))?")
    L_COMMAND_REGREP = re.compile('^\([\w\.\$:]*\)$')

    def __init__(self, filename: str):
        self.filename = filename
        self.file = open(filename, "r")
        self.command = None

    def hasMoreCommand(self, line: str):
        return True if line != '' else False

    def advance(self):
        while True:
            line = self.file.readline()
            logging.debug("readline: {}".format(line))
            if not line:
                self.command = None
                break

            line = re.sub('[\s]', '', line)
            line_fin = line.find('//')
            if line_fin != -1:
                line = line[:line_fin]
            if line:
                logging.debug("set command: {}".format(line))
                self.command = line
                return True

        return False

    def commandType(self):
        logging.debug("comandType: {}".format(self.command))
        if self.A_COMMAND_REGREP_SYMBOL.match(self.command) is not None:
            return self.A_COMMAND
        elif self.A_COMMAND_REGREP_NUM.match(self.command) is not None:
            return self.A_COMMAND
        elif self.L_COMMAND_REGREP.match(self.command) is not None:
            return self.L_COMMAND
        else:
            return self.C_COMMAND

    def symbol(self):
        if self.command[0] is "@":
            return self.command[1:]
        elif self.command[0] is "(" and self.command[-1] is ")":
            return self.command[1:-1]
        else:
            raise Exception()

    def dest(self):
        d = re.match(self.C_COMMAND_REGREP, self.command)
        ret = d.group(1) if d is not None else None
        return ret if ret is not None else ""

    def comp(self):
        d = re.match(self.C_COMMAND_REGREP, self.command)
        ret = d.group(2) if d is not None else None
        return ret if ret is not None else ""

    def jump(self):
        d = re.match(self.C_COMMAND_REGREP, self.command)
        ret = d.group(3) if d is not None else None
        return ret if ret is not None else ""