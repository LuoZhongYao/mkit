import subprocess
import os
import sys

class ShellError(Exception) :
    def __init__(self,cmd,out,err) :
        self.cmd,self.out,self.err = cmd,out,err
    def __str__(self):
        return " ".join(self.cmd) + '\n' + self.out  + '\n' + self.err + '\n'

class Shell() :
    def __init__(self) : pass

    def exec(self,cmd) :
        cmd[0] = cmd[0]
        sub = subprocess.Popen(cmd,shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True)
        ret = sub.wait()
        out,err = sub.communicate()
        if ret :
            raise ShellError(cmd,out,err)
        return out
