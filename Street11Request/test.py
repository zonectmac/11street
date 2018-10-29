import subprocess

dict = {}
dict["x61"] = "P11"
dict["x62"] = "P22"
dict["x63"] = "P33"

sdict = str(dict)

subprocess.call(['cscript.exe', 'C:\\Users\\Administrator\\Desktop\\新建文件夹\\123.vbs', sdict])
