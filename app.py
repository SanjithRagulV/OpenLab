# Importing flask module in the project is mandatory
from flask import Flask, render_template, request, url_for, redirect, session
from graphviz import Digraph, nohtml
import os
from typing import DefaultDict
from urllib.parse import urlsplit, parse_qs, urlparse, urlunparse
from urllib.request import urlopen
import urllib.robotparser
from bs4 import BeautifulSoup
from urllib3.exceptions import HTTPError

app = Flask(__name__)

MORSE_CODE_DICT = {'A': '.-', 'B': '-...',
                   'C': '-.-.', 'D': '-..', 'E': '.',
                   'F': '..-.', 'G': '--.', 'H': '....',
                   'I': '..', 'J': '.---', 'K': '-.-',
                   'L': '.-..', 'M': '--', 'N': '-.',
                   'O': '---', 'P': '.--.', 'Q': '--.-',
                   'R': '.-.', 'S': '...', 'T': '-',
                   'U': '..-', 'V': '...-', 'W': '.--',
                   'X': '-..-', 'Y': '-.--', 'Z': '--..',
                   '1': '.----', '2': '..---', '3': '...--',
                   '4': '....-', '5': '.....', '6': '-....',
                   '7': '--...', '8': '---..', '9': '----.',
                   '0': '-----', ', ': '--..--', '.': '.-.-.-',
                   '?': '..--..', '/': '-..-.', '-': '-....-',
                   '(': '-.--.', ')': '-.--.-'}

letters = "-ETIANMSURWDKGOHVF*L*PJBXCYZQ**54*3***2**+****16=/*****7***8*90"


def morseToString(morse):
    index = 1
    message = ""
    for i in range(len(morse)):
        if i < len(morse) - 1:
            if morse[i] == " ":
                message += letters[index - 1]
                index = 1
            elif morse[i] == ".":
                index = 2 * index
                if (index > len(letters)):
                    break
            elif morse[i] == "-":
                index = 2 * index + 1
                if (index > len(letters)):
                    break
        else:
            if morse[i] == ".":
                index = 2 * index
                if (index > len(letters)):
                    break
            elif morse[i] == "-":
                index = 2 * index + 1
                if (index > len(letters)):
                    break
            message += letters[index - 1]
            index = 1
    return message.replace("*", " ")


def encrypt(message):
    cipher = ''
    for letter in message:
        if letter != ' ':
            cipher += MORSE_CODE_DICT[letter] + ' '
        else:
            cipher += ' '

    return cipher


class Node:
    n = 0

    def __init__(self, scala=3):
        self.values = []
        self.parent = None
        Node.n += 1
        self.id = Node.n
        self.children = []

    def insert(self, value):
        if value in self.values:
            s = 0
        else:
            self.values.append(value)
            self.values.sort()
        return len(self.values)

    def compare(self, value):
        length = len(self.values)
        if self.children == [] or value in self.values:
            return None

        for i in range(length):
            if value < self.values[i]:
                return i
        return i + 1

    def getPos(self):
        return self.parent.children.index(self)

    def getValLen(self):
        return len(self.values)


class BTree:
    def __init__(self, node: Node = None, scala=3):
        self.root = Node(scala=scala)
        self.scala = scala
        self.mid_index = int((self.scala - 1) / 2)
        a = []

    def find(self, value, node: Node = None):
        if not node:
            _node = self.root
        else:
            _node = node

        result = _node.compare(value)
        if result is None:
            return _node
        else:
            return self.find(value, node=_node.children[result])

    def _split(self, node):
        if len(node.values) <= self.scala - 1:
            return 0

        '''spliting the node'''
        parent = node.parent
        new_node, l_node, r_node = Node(), Node(), Node()

        mid_index = self.mid_index
        l_node.values = node.values[0:mid_index]
        center = node.values[mid_index]
        r_node.values = node.values[mid_index + 1:]

        '''if the parent needs to be split
        1,2,3,6,7,8 and add 5'''

        if node.children:
            l_node.children = node.children[0:mid_index + 1]
            r_node.children = node.children[mid_index + 1:]
            for i in range(mid_index + 1):
                node.children[i].parent = l_node
            for i in range(mid_index + 1, self.scala + 1):
                node.children[i].parent = r_node

        '''root'''
        if not parent:
            parent = new_node
            parent.values.append(center)
            parent.children.insert(0, l_node)
            parent.children.insert(1, r_node)
            l_node.parent = parent
            r_node.parent = parent
            self.root = parent
            return 0

        '''insert into parent spliting the leaves'''
        l_node.parent = parent
        r_node.parent = parent
        parent.insert(center)
        index = parent.children.index(node)
        parent.children.pop(index)
        parent.children.insert(index, l_node)
        parent.children.insert(index + 1, r_node)
        return self._split(parent)

    def insert(self, *values):
        for value in values:
            node = self.find(value)
            length = node.insert(value)

            if length == self.scala:
                self._split(node)

    def print_order(self):
        a = []
        b = []
        this_level = [self.root]
        while this_level:
            next_level = []
            output = ""
            for node in this_level:
                if node.children:
                    next_level.extend(node.children)
                for s in node.values:
                    b.append(s)
                output += str(node.values) + " "

            a.append(output)

            this_level = next_level
        return b

    def stepCover(self, node: Node, value_pos):  # value_pos indicates the position of the deleted value
        if not node.children:
            return self.merge(node, node.getPos())

        after = node.children[value_pos + 1]
        node.insert(after.values.pop(0))
        return self.stepCover(after, 0)

    def merge(self, node, pos):
        if not node.parent:
            return 0

        if node.getValLen() >= self.mid_index:
            return 0

        parent = node.parent
        if pos:
            pre = parent.values[pos - 1]
            bnode = parent.children[pos - 1]
        else:
            pre = None
            bnode = parent.children[1]

        if bnode.getValLen() > self.mid_index:
            return self.rotate(node, bnode, parent, pre)

        if not pre:
            node.insert(parent.values.pop(0))
            bnode.children = node.children + bnode.children
        else:
            node.insert(parent.values.pop(pos - 1))
            bnode.children = bnode.children + node.children
        bnode.values += node.values
        bnode.values.sort()
        parent.children.remove(node)
        if parent.getValLen() == 0 and not parent.parent:
            self.root = bnode
            return 0

        if parent.getValLen() < self.mid_index:
            return self.merge(parent, parent.getPos())

    def rotate(self, node, bnode, parent, pre):
        if not pre:
            return self.leftRotate(node, bnode, parent)
        return self.rightRotate(node, bnode, parent)

    def leftRotate(self, node, bnode, parent):
        node.insert(parent.values.pop(0))
        parent.insert(bnode.values.pop(0))
        return 0

    def rightRotate(self, node, bnode, parent):
        pos = node.getPos()
        node.insert(parent.values.pop(pos - 1))
        parent.insert(bnode.values.pop(-1))
        return 0

    def delete(self, value):
        node = self.find(value)
        value_pos = node.values.index(value)
        node.values.remove(value)
        self.stepCover(node, value_pos)

    def _find(self, value, node: Node = None):
        if not node:
            return BTree.compare(value, self.root)
        else:
            return BTree.compare(value, node)

    def grap(self, nod):
        for m in nod:
            nst = ''
            for l in m.values:
                cn = m.values.index(l)
                if cn > 0:
                    nst += '|'
                nst += str(l)
            g.node('node' + str(m.id), nohtml(nst))
            if (m.parent is not None) and (len(m.parent.values) != 0):
                g.edge('node' + str(m.parent.id), 'node' + str(m.id))
            self.grap(m.children)

    def gra(self):
        global g
        g = Digraph('g', filename='btree.gv',
                    node_attr={'shape': 'record', 'height': '.1'}, directory="C:/Users/HP/PycharmProjects"
                                                                             "/pythonProject/static", format='jpeg')
        self.grap([self.root])
        g.view()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ws')
def ws():
    return render_template('webscrap.html', d=dict)


@app.route('/insert', methods=['POST'])
def insert():
    if request.method == "POST":
        insert_key = request.form.get("it")
        if insert_key:
            btree.insert(int(insert_key))
            os.remove("static/btree.gv.jpeg")
            btree.gra()
    return render_template('pass.html')


@app.route('/delete', methods=['POST'])
def delete():
    if request.method == "POST":
        delete_key = request.form.get("dt")
        if delete_key:
            b = btree.print_order()
            if int(delete_key) in b:
                btree.delete(int(delete_key))
                os.remove("static/btree.gv.jpeg")
                btree.gra()
    return render_template('pass.html')


@app.route('/search', methods=['POST'])
def search():
    if request.method == "POST":
        search_key = request.form.get("st")
        if search_key:
            b = btree.print_order()
            if int(search_key) in b:
                print("pop.html")
                return render_template('pop.html')
            else:
                return render_template('pop1.html')
    return render_template('pass.html')


@app.route("/home", methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/morse', methods=["POST", "GET"])
def morse():
    if request.method == "POST":
        decoded = ""
        converted = ""
        stringconvert = request.form.get("stringconvert")
        morse = request.form.get("morsecode")
        if (morse != None):
            decoded = morseToString(morse)
            stringconvert = ""
        elif (stringconvert != None):
            converted = encrypt(stringconvert.upper())
            morse = ""
        return render_template('morse.html', decoded=decoded, stringconvert=converted, mor=morse, str=stringconvert)
    if request.method == "GET":
        return render_template('morse.html', decoded="", stringconvert="", mor="", str="")


if __name__ == '__main__':
    global i
    i = 0
    dict = {}
    try:
        html = urlopen("https://www.tutorialspoint.com/the-b-tree-in-data-structure")
        parse_url = urlparse("https://www.tutorialspoint.com/the-b-tree-in-data-structure")
        print()
        print("Using URLLIB:")
        print(parse_url)
        unparse_url = urlunparse(parse_url)
        print(unparse_url)
        print()
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url("https://www.tutorialspoint.com/the-b-tree-in-data-structure/robots.txt")
        rp.read()
        print("ROBOT PARSER:")
        print(rp.can_fetch("*", "https://www.tutorialspoint.com/the-b-tree-in-data-structure"))
        print()

    except HTTPError as e:
        print(e)
    else:
        print("Using BeautifulSoup:")
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string
        if title is None:
            print("Title could not be found")
        else:
            dict['title'] = title
            print(title)
        dict['references'] = []
        print("REFERENCES:")
        for link in soup.find_all('a')[0:10]:
            print(link.get('href'))
            dict['references'].append(link.get('href'))
        x = soup.find_all("div", class_="mui-col-md-6 tutorial-content")
        print("Introduction:")
        print(len(x))
        for i in x:
            intro = i.p
            print(i.p.string)
            dict['intro'] = i.p.string
        print("Properties:")
        dict['properties'] = []
        print(intro.next_sibling.string)
        count = 0
        children = soup.find("ul", {"class": "list"}).findAll("li")
        for child in children:
            print(i, ")", child.p.string)
            dict['properties'].append(child.p.string)
    print()
    r = soup.find("ul", class_="toc chapters").findAll("li")
    for i in r[4:5]:
        route1 = i.a['href']
        print(route1)
    try:
        html = urlopen(route1)
    except HTTPError as e:
        print(e)
    else:

        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string
        if title is None:
            print("Title could not be found")
        else:
            dict['title2'] = title
            print(title)
        x = soup.find("div", class_="mui-col-md-6 tutorial-content").findAll("p")
        for i in x[4:5]:
            dict['intro2'] = i.string
            print(i.string)
        print("ALGORITHM:INSERT")
        x = soup.find("div", class_="mui-col-md-6 tutorial-content").findAll("pre")
        for i in x:
            dict['ALGORITHM:INSERT'] = i.string
            print(i.string)
    print()

    for i in r[2:3]:
        route2 = i.a['href']
        print(route2)

    try:
        html = urlopen(route2)
    except HTTPError as e:
        print(e)
    else:
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string
        if title is None:
            print("Title could not be found")
        else:
            dict['title3'] = title
            print(title)
        x = soup.find("div", class_="mui-col-md-6 tutorial-content").findAll("p")
        for i in x[3:5]:
            dict['intro3'] = i.string
            print(i.string)
        print("ALGORITHM:DELETE")
        x = soup.find("div", class_="mui-col-md-6 tutorial-content").findAll("pre")
        for i in x:
            dict['ALGORITHM:DELETE'] = i.string
            print(i.string)

    print()

    for i in r[3:4]:
        route3 = i.a['href']
        print(route3)
    try:
        html = urlopen(route3)
    except HTTPError as e:
        print(e)
    else:
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string
        if title is None:
            print("Title could not be found")
        else:
            dict['title4'] = title
            print(title)
        x = soup.find("div", class_="mui-col-md-6 tutorial-content").findAll("p")
        for i in x[3:5]:
            dict['intro4'] = i.string
            print(i.string)
        print("ALGORITHM:SEARCH")
        x = soup.find("div", class_="mui-col-md-6 tutorial-content").findAll("pre")
        for i in x:
            dict['ALGORITHM:SEARCH'] = i.string
            print(i.string)

    btree = BTree(scala=3)
    app.run(debug=True)
