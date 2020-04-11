import Parser
import CodeWriter
from CommandType import CommandType
import argparse
import os
import glob


class VMtranslator():
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Transrate VM file or directory to single asm file.')
        self.parser.add_argument('path', type=str, help='vm file or directory')
        args = self.parser.parse_args()
        path = args.path

        if os.path.isfile(path):
            if path.endswith('.vm'):
                self.code_writer = CodeWriter.CodeWriter(
                    "{}.asm".format(path[:-3]))
                self.files = [path]
            else:
                raise Exception("path: file name should end with \".vm\".")
        elif os.path.isdir(path):
            if path.endswith('/'):
                path = path[:-1]
            self.code_writer = CodeWriter.CodeWriter("{}.asm".format(path))
            self.files = glob.glob(f"{path}/*.vm")
        else:
            raise Exception("Unsupport File Type.")

    def translate(self):
        for f in self.files:
            filename = os.path.basename(f)
            self.code_writer.setFileName(filename)
            self.parser = Parser.Parser(f)
            while self.parser.advance():
                cmd_type = self.parser.commandType()
                print(f"{cmd_type} : {self.parser.command}")
                self.code_writer.writeComment(
                    f"{filename}: {self.parser.command} (line: {self.parser.line})")
                if cmd_type == CommandType.C_ARITHMETIC:
                    self.code_writer.writeArithmetic(self.parser.arg1())
                elif cmd_type in [CommandType.C_PUSH, CommandType.C_POP]:
                    self.code_writer.writePushPop(
                        cmd_type, self.parser.arg1(), self.parser.arg2())
                elif cmd_type == CommandType.C_LABEL:
                    self.code_writer.writeLabel(self.parser.arg1())
                elif cmd_type == CommandType.C_GOTO:
                    self.code_writer.writeGoto(self.parser.arg1())
                elif cmd_type == CommandType.C_IF:
                    self.code_writer.writeIf(self.parser.arg1())
                elif cmd_type == CommandType.C_FUNCTION:
                    self.code_writer.writeFunction(
                        self.parser.arg1(), self.parser.arg2())
                elif cmd_type == CommandType.C_CALL:
                    self.code_writer.writeCall(
                        self.parser.arg1(), self.parser.arg2())
                elif cmd_type == CommandType.C_RETURN:
                    self.code_writer.writeReturn()
                else:
                    raise Exception(
                        "Parser Error: command: {}".format(self.parser.command))
            self.parser = None
        self.code_writer.close()


if __name__ == '__main__':
    VMtranslator().translate()
