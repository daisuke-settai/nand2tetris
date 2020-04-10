import re
from CommandType import CommandType

CMD_TYPE_REGREPS = {
    CommandType.C_ARITHMETIC: re.compile("^((?:add)|(?:sub)|(?:neg)|(?:eq)|" +\
    "(?:gt)|(?:lt)|(?:and)|(?:or)|(?:not))$"),
    CommandType.C_PUSH: re.compile("^push[\s]+([\w]+)[\s]+([\d]+)$"),
    CommandType.C_POP: re.compile("^pop[\s]+([\w]+)[\s]+([\d]+)$"),
    CommandType.C_LABEL: re.compile("^$"),
    CommandType.C_GOTO: re.compile("^$"),
    CommandType.C_IF: re.compile("^$"),
    CommandType.C_FUNCTION: re.compile("^$"),
    CommandType.C_RETURN: re.compile("^$"),
    CommandType.C_CALL: re.compile("^$"),
}

class Parser():

    def __init__(self, file: str):
        self.file = open(file, "r")
        self.command = None
        self.command_type = None
        self.command_matched = None

    def advance(self) -> bool:
        """
        次のコマンドを用意
        """
        while True:
            line = self.file.readline()
            if not line:
                self.command = None
                return False
            line = line.strip()
            comment_i = line.find("//")
            if comment_i != -1:
                line = line[:comment_i]
            if len(line) == 0:
                continue
            self.command = line
            return True

    def commandType(self) -> int:
        """
        vmコマンドの種類を返す
        """
        for t, r in CMD_TYPE_REGREPS.items():
            matched_re = r.match(self.command)
            if matched_re:
                self.command_type = t
                self.command_matched = matched_re
                return t

    def arg1(self) -> str:
        """
        最初の引数が返される
        """
        return self.command_matched.group(1)

    def arg2(self) -> int:
        """
        2番目の引数が返される
        """
        return int(self.command_matched.group(2))
