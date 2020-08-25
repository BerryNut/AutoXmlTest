#coding:utf-8
import xml
import xml.etree.ElementTree as ET
import re
import sys
reload(sys)
sys.setdefaultencoding('utf8')  
"""
实现从xml文件中读取ref数据并输出自动化测试代码
"""
# attribList = ["publication-type" ]

def xpathProcess(node, xpath, flag, lable):
  xpath = xpath +"/"
  if node.tag != "citation-alternatives":
    xpath = xpath + str(node.tag)

  if node.tag == "ref" :
    lable = node.attrib["id"][1:]
    xpath = xpath + "[" +lable+ "]"
  # elif node.attrib != None:
  #   print(node.attrib)
  elif flag != 0: 
    xpath = xpath +  "[" +str(flag)+ "]"
  return xpath,lable

def write(node, xpath, lable, flag):
  name = node.tag
  content = node.text
  f = open('ans.robot','a') 
  f.write("验证第" + lable+"条参考文献"+name)
  if flag > 1  :
    f.write(str(flag))
  f.write("\n" + "    Jats Text Should Be         ")
  f.write(xpath)
  if(name == "uri" or name == "ext-link"):
    # print(node.attrib)
    content = node.attrib["{http://www.w3.org/1999/xlink}href"]
    f.write('[@${XLINK}href="'+ content + '"]')
  f.write("         ")
  f.write(content + "\n\n") 
  return

def writeMix(node, xpath, lable):
  name = node.tag
  att = node.attrib
  f = open('ans.robot','a') 
  f.write("验证第" + lable+"条参考文献类型" + "\n")
  f.write("    Jats Elements Attribute     ")
  f.write(xpath)
  f.write("   publication-type        ")
  f.write(att["publication-type"] + "\n\n") 

  f.write("验证第" + lable+"条参考文献格式" + "\n")
  f.write("    Jats Elements Attribute     ")
  f.write(xpath)
  f.write("   publication-format      ")
  f.write(att["publication-format"] + "\n\n")
  return

#遍历所有的节点 
def walkData(node, xpath, flag, lable): 
  xpath, lable = xpathProcess(node, xpath, flag, lable)
  if(node.tag == "mixed-citation"):
    writeMix(node, xpath, lable)
  #遍历每个子节点 
  children_node = node.getchildren() 

  if(len(children_node) == 0): 
    # 无子节点 输出
    write(node, xpath, lable, flag)
  elif(len(children_node) == 1):
    # 只有一个子节点，向下遍历
    walkData(children_node[0], xpath, 0, lable)
  else :
    # 子节点大于1 
    for child in children_node:
      flag = 0
      for samechild in children_node:
        if child.tag == samechild.tag:
          flag = flag+1
      if(flag == 1): flag = 0
      # 存在同名子节点：获取同名子节点的序号
      if flag > 1 :
        flag = 0
        for samechild in children_node:
          if child.tag == samechild.tag:
            flag = flag+1
          if child.getchildren() is samechild.getchildren():
            break
      walkData(child, xpath, flag, lable)
      
  return
 
def getXmlData(file_name,module):
  xpath = ".//ref-list"
  root = ET.parse(file_name).getroot()
  for node in root.iter(module):
    walkData(node, xpath, 0, "")

  return 

def getAll(file_name):
  xml = open(file_name, "r")   # 打开文件
  data = xml.read()  # 读取文件
  lable = re.search('<label>[0-9]+',data)  
  lable = lable.group(0)[7:]     #获取标签名
  data = data.replace("\n","")
  data = data.replace("\t","")  #删除格式
  while "<" in data  :  # 删除标签
    start = data.index("<")
    end = data.index(">")
    data = data[:start] + data[end+1:]
  f = open('ans.robot','a')
  f.write("验证第" + lable+"条参考文献all")
  f.write("\n" + "    Jats Text Should Be         ")
  f.write(".//ref-list/ref[" + lable + "]")
  f.write("         " + data + "\n\n")

if __name__ == '__main__':
  
  file_name = 'test.xml'

  R = getXmlData(file_name,'ref')   
  getAll(file_name)
    # for x in R: 
    #   print(x)
    # getcase(R)
