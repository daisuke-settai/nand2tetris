from CommandType import CommandType


class CodeWriter():
    # M: arg1, D: arg2
    arithmetic_commands = {
        'add': 'D=D+M',  # binary command
        'sub': 'D=M-D',
        'and': 'D=D&M',
        'or':  'D=D|M',
        'not': 'D=!M',  # unary command
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

    ENTRY_POINT = "Sys.init"

    def __init__(self, filename: str):
        self.dst_file = open(filename, "w")
        self.filename = None
        self.label_count = 0
        self.return_label_count = 0
        self.function_name = None

        self.writeInit()

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
            raise Exception(
                'Unsupported Command: {c}\n\tOriginal Error: {e}'.format(c=command, e=e))

    def writePushPop(self, command: int, segment: str, index: int):
        """
        C_[PUSH, POP]コマンドをアセンブリに変換し出力
        """
        self.writeCode([
            "// {c} {s} {i}".format(c="push" if command ==
                                    CommandType.C_PUSH else 'pop', s=segment, i=index)
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
                    '@{filename}.{index}'.format(
                        filename=self.filename, index=index),
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
                    '@{filename}.{index}'.format(
                        filename=self.filename, index=index),
                    'M=D',
                ])
        else:
            raise Exception("Unsupport command: {}".format(command))

    def close(self):
        """
        出力ファイルを閉じる
        """
        self.dst_file.close()

    def writeInit(self):
        """
        VMの初期化コードを出力
        出力ファイルの先頭に配置される
        """
        self.writeSetSP(256)
        self.writeCall(self.ENTRY_POINT, 0)

    def writeLabel(self, label: str):
        """
        labelコマンドを出力
        """
        self.writeCode([
            f"({self.function_name}${label})"
        ])

    def writeGoto(self, label: str):
        """
        gotoコマンドを出力
        """
        self.writeCode([
            f"@{self.function_name}${label}",
            '0;JMP'
        ])

    def writeIf(self, label: str):
        """
        if-gotoコマンドを出力
        """
        self.writePopToM()
        self.writeCode([
            'D=M',
            f"@{self.function_name}${label}",
            'D;JNE'
        ])

    def writeCall(self, functionName: str, numArgs: int = 0):
        """
        callコマンドを出力
        """
        return_label = self.getReturnLabel()
        self.writeCode([
            f"@{return_label}",
            'D=A'
        ])
        self.writePushFromD()
        # Save State
        for l in ['@LCL', '@ARG', '@THIS', '@THAT']:
            self.writeCode([
                l,
                'D=M'
            ])
            self.writePushFromD()
        self.writeCode([
            '//    SET ARG',
            '@SP',
            'D=M',
            '@{}'.format(5 + numArgs),
            'D=D-A',
            '@ARG',
            'M=D',
            '//    SET LCL',
            '@SP',
            'D=M',
            '@LCL',
            'M=D',
            f"@{functionName}",
            '0;JMP',
            f"({return_label})"
        ])

    def writeReturn(self):
        """
        returnコマンドを出力
        """
        # ステートを戻して, リターンアドレスにジャンプ
        self.writeCode([
            '//    FRAME -> R13',
            '@LCL',
            'D=M',
            '@R13',
            'M=D',
            '//    return address -> R14',
            '@5',
            'D=A',
            '@R13',
            'A=M-D',
            'D=M',
            '@R14',
            'M=D',
            '//    pop() -> *ARG',
        ])
        self.writePopToM()
        self.writeCode([
            'D=M',
            '@ARG',
            'A=M',
            'M=D',
            '//    ARG + 1 -> SP',
            '@ARG',
            'D=M+1',
            '@SP',
            'M=D',
            '//    State Load',
        ])
        for l in ['@THAT', '@THIS', '@ARG', '@LCL']:
            self.writeCode([
                '@R13',
                'AM=M-1',
                'D=M',
                l,
                'M=D',
            ])
        self.writeCode([
            '//    jump to return-address',
            '@R14',
            'A=M',
            '0;JMP'
        ])

    def writeFunction(self, functionName: str, numLocals: int):
        """
        functionコマンドを出力
        """
        self.writeCode([
            f"({functionName})",
            '//    allocate local var space',
            'D=0'
        ])
        for i in range(numLocals):
            self.writePushFromD()

        self.function_name = functionName

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
            'D=0',  # set False
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
            '//    pop to m',
            '@SP',
            'AM=M-1',
        ])

    def writePushFromD(self):
        """
        DからSPの位置へ値を書き込み, SPを+1
        """
        self.writeCode([
            '//    push from d',
            '@SP',  # Aに0を代入
            'A=M',
            'M=D',
            '@SP',
            'M=M+1'
        ])

    def writeSetSP(self, address):
        self.writeCode([
            f"@{address}",
            'D=A',
            '@SP',
            'M=D'
        ])

    def writeCode(self, codes: list):
        self.dst_file.write('\n'.join(codes) + '\n')

    def getLabel(self):
        self.label_count += 1
        return f"LABEL{self.label_count}"

    def getReturnLabel(self):
        self.return_label_count += 1
        return f"RETURN{self.return_label_count}"
    
    def writeComment(self, comment: str):
        self.writeCode([f"// {comment}"])
