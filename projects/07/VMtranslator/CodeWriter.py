from CommandType import CommandType

class CodeWriter():
    # M: arg1, D: arg2
    arithmetic_commands = {
        'add': 'D=D+M', # binary command
        'sub': 'D=M-D',
        'and': 'D=D&M',
        'or':  'D=D|M',
        'not': 'D=!M', # unary command
        'neg': 'D=-M',
        'eq':  'JEQ',  # comp command
        'gt':  'JGT',
        'lt':  'JLT',
    }
    segment_names = {
        'local':    'LCL',
        'argument': 'ARG',
        'this':     'THIS',
        'that':     'THAT',
        'temp':     '5',
        'pointer':  '3',
    }

    def __init__(self, filename: str):
        self.dst_file = open(filename, "w")
        self.filename = None
        self.label_count = 0

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, trace):
        self.dst_file.close()

    def setFileName(self, fileName: str):
        """
        CodeWriterモジュールに新しいVMファイルの変換が開始したことを知らせる
        """
        self.filename = fileName

    def writeArithmetic(self, command: str):
        """
        算術コマンドをアセンブリに変換し出力
        """
        self.writeCode([
            f"// {command}"
        ])
        try:
            if command in ['add', 'sub', 'and', 'or']:
                self.writeArithmeticBinary(command)
            elif command in ['neg', 'not']:
                self.writeArithmeticSingle(command)
            elif command in ['eq', 'gt', 'lt']:
                self.writeArithmeticComp(command)
            else:
                raise Exception("Unsupport command: {}".format(command))
        except KeyError as e:
            raise Exception('Unsupported Command: {c}\n\tOriginal Error: {e}'.format(c=command, e=e))

    def writePushPop(self, command: int, segment: str, index: int):
        """
        C_[PUSH, POP]コマンドをアセンブリに変換し出力
        """
        self.writeCode([
            "// {c} {s} {i}".format(c="push" if command == CommandType.C_PUSH else 'pop', s=segment, i=index)
        ])
        if command == CommandType.C_PUSH:
            if segment == 'constant':
                self.writeCode([
                    f"@{index}",
                    "D=A",
                ])
                self.writePushFromD()
            elif segment in ['local', 'argument', 'this', 'that']:
                self.writePushFromVirtualSegment(segment, index)
            elif segment in ['temp', 'pointer']:
                self.writePushFromStaticSegment(segment, index)
            elif segment == 'static':
                self.writeCode([
                    '@{filename}.{index}'.format(filename=self.filename, index=index),
                    'D=M'
                ])
                self.writePushFromD()
        elif command == CommandType.C_POP:
            if segment in ['local', 'argument', 'this', 'that']:
                self.writePopToVritualSegment(segment, index)
            elif segment in ['temp', 'pointer']:
                self.writePopToStaticSegment(segment, index)
            elif segment == 'static':
                self.writePopToM()
                self.writeCode([
                    'D=M',
                    '@{filename}.{index}'.format(filename=self.filename, index=index),
                    'M=D',
                ])
        else:
            raise Exception("Unsupport command: {}".format(command))

    def close(self):
        """
        出力ファイルを閉じる
        """
        self.dst_file.close()

    # 最適化後は "add": "@SP\nA=M-1\nD=M\nA=A-1\nM=M+D\n@SP\nM=M-1\n",
    # しかし, コードをシンプルに
    def writeArithmeticBinary(self, command: str):
        self.writePopToM()
        self.writeCode([
            'D=M'
        ])
        self.writePopToM()
        self.writeCode([
            self.arithmetic_commands[command]
            ])
        self.writePushFromD()        

    def writeArithmeticSingle(self, command: str):
        self.writePopToM()
        self.writeCode([
            self.arithmetic_commands[command],
            ])
        self.writePushFromD()

    def writeArithmeticComp(self, command: str):
        self.writePopToM()
        self.writeCode([
            'D=M'
        ])
        self.writePopToM()
        goto_true = self.getLabel()
        goto_false = self.getLabel()
        comp_type = self.arithmetic_commands[command]
        self.writeCode([
            'D=M-D',
            f"@{goto_true}",
            f"D;{comp_type}",
            'D=0', # set False
            f"@{goto_false}",
            '0;JMP',
            f"({goto_true})",
            'D=-1',  # set True
            f"({goto_false})"
        ])
        self.writePushFromD()

    def writePushFromVirtualSegment(self, segment: str, index: int):
        self.writeCode([
            '@{}'.format(self.segment_names[segment]),
            'A=M',
            *(['A=A+1'] * index),
            'D=M',
        ])
        self.writePushFromD()

    def writePopToVritualSegment(self, segment: str, index: int):
        self.writePopToM()
        self.writeCode([
            'D=M',
            '@{}'.format(self.segment_names[segment]),
            'A=M',
            *(['A=A+1'] * index),
            'M=D'
        ])

    def writePushFromStaticSegment(self, segment: str, index: int):
        self.writeCode([
            '@{}'.format(self.segment_names[segment]),
            *(['A=A+1'] * index),
            'D=M',
       ])
        self.writePushFromD()
    
    def writePopToStaticSegment(self, segment: str, index: int):
        self.writePopToM()
        self.writeCode([
            'D=M',
            '@{}'.format(self.segment_names[segment]),
            *(['A=A+1'] * index),
            'M=D',
        ])

    def writePopToM(self):
        """
        SPをスタックの最上位の要素に合わせて, その値をAに設定
        """
        self.writeCode([
            '@SP',
            'AM=M-1',
        ])

    def writePushFromD(self):
        """
        DからSPの位置へ値を書き込み, SPを+1
        """
        self.writeCode([
            '@SP', # Aに0を代入
            'A=M',
            'M=D',
            '@SP',
            'M=M+1'
        ])

    def writeCode(self, codes: list):
        self.dst_file.write('\n'.join(codes) + '\n')

    def getLabel(self):
        self.label_count += 1
        return f"LABEL{self.label_count}"