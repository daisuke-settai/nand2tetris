import Parser
import CodeWriter
from CommandType import CommandType
import argparse
import os 
import glob

class VMtranslator():
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Transrate VM file or directory to single asm file.')
        self.parser.add_argument('path', type=str, help='vm file or directory')
        args = self.parser.parse_args()
        path = args.path

        if os.path.isfile(path):
            if path.endswith('.vm'):
                self.code_writer = CodeWriter.CodeWriter("{}.asm".format(path[:-3]))
                self.files = [path]
            else:
                raise Exception("path: file name should end with \".vm\".")
        elif os.path.isdir(path):
            if path.endswith('/'):
                path = path[:-1]
            self.code_writer = CodeWriter.CodeWriter("{}.asm".format(path))
            self.files = glob.glob(f"{path}/*")
        else:
            raise Exception("Unsupport File Type.")

    def translate(self):
        for f in self.files:
            filename = os.path.basename(f)
            self.code_writer.setFileName(filename)
            self.parser = Parser.Parser(f)
            while self.parser.advance():
                cmd_type = self.parser.commandType()
                if cmd_type == CommandType.C_ARITHMETIC:
                    print(self.parser.command + " Arithmetic: " + str(cmd_type))
                    self.code_writer.writeArithmetic(self.parser.arg1())
                elif cmd_type in [ CommandType.C_PUSH, CommandType.C_POP ]:
                    self.code_writer.writePushPop(cmd_type, self.parser.arg1(), self.parser.arg2())
                else:
                    raise Exception("Parser Error: command: {}".format(self.parser.command))
            self.parser = None
        self.code_writer.close()


if __name__ == '__main__':
    VMtranslator().translate()