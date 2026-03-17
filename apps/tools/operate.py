import string
import random
from time import time_ns
from django.db.models import Model
from django.utils import timezone
#import datetime


class Id:
    def generate(length:int):
        alphabet_lower = list(string.ascii_lowercase)
        alphabet_upper = list(string.ascii_uppercase)
        numbers = [str(i) for i in range(9)]
        specials = ['!','@','#','_','-','<','>']
        symbols = alphabet_lower + alphabet_upper + numbers #+ specials
        random.seed(time_ns())
        return ''.join(random.choices(symbols,k=length))

    def isvalid(target:Model,target_id):
        return target.objects.filter(target_id=target_id).count() == 0


DEFAULT_TIME_LENGTH = 30   
"""def start_time(): return datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0)
def deadline(startfrom:datetime.datetime=None,period_in_days=None):
    if isinstance(startfrom,datetime.datetime) and isinstance(period_in_days,int):
        return startfrom + datetime.timedelta(days=period_in_days)
    return start_time() + datetime.timedelta(days=DEFAULT_TIME_LENGTH)
"""
def start_time(): return timezone.now()
def deadline(startfrom:timezone=None,period_in_days=None):
    if isinstance(startfrom,timezone.datetime) and isinstance(period_in_days,int):
        return startfrom + timezone.timedelta(days=period_in_days)
    return start_time() + timezone.timedelta(days=DEFAULT_TIME_LENGTH)


class StringBox:
    divider = '+'
    def get_elements(box:str)->list:
        return box.split(StringBox.divider)
    def create(content:list)->list:
        if len(content) == 0: return ""
        else: 
            elements = ''
            for element in content:
                elements += element + StringBox.divider
            elements = elements[:-1]
    def add(box:str,element:str)->str:
        if len(box) == 0: return element
        else:
            return box + StringBox.divider + element
    def clear(): return ""
    def remove(box:str,element:str):
        content:list = StringBox.get_elements(box)
        if element in content:
            content.remove(element)
        return StringBox.create(content)
    
class Node:
    
    def __init__(self, word) -> None:
        self.word = word
        self.right = None
        self.left = None
        self.adjacent_dictionary = {}

    def insert(self, word):
        if word <= self.word:
            if self.left is None:
                self.left = Node(word)
            else:
                self.left.insert(word)
        else:
            if self.right is None:
                self.right = Node(word)
            else:
                self.right.insert(word)
    #create dictionary with nodes and their children
    def create_adjacent(self,node):
        if node is None: return
        self.adjacent_dictionary[node.word] = []
        
        if node.left is not None: self.adjacent_dictionary[node.word].append(node.left.word)
        if node.right is not None: self.adjacent_dictionary[node.word].append(node.right.word)
        
        self.create_adjacent(node.left)
        self.create_adjacent(node.right)
    def breadth_first_search(self):
        if not self.adjacent_dictionary: self.create_adjacent(self)
        queue = [self.word,]
        visited = []
        while queue:
            node = queue.pop(0)
            visited.append(node)
            [queue.append(word) for word in self.adjacent_dictionary[node]]
        return visited
    @staticmethod
    def in_order(node):
        if node is None: return
        if not isinstance(node,Node): return
        Node.in_order(node.left)
        print(node.word, end=' ')
        Node.in_order(node.right)
    @staticmethod
    def pre_order(node):
        if node is None: return
        if not isinstance(node,Node): return
        print(node.word, end=' ')
        Node.pre_order(node.left)
        Node.pre_order(node.right)
    @staticmethod
    def post_order(node):
        if node is None: return
        if not isinstance(node,Node): return
        print(node.word, end=' ')
        Node.post_order(node.right)
        Node.post_order(node.left)

class Word:
    import math
    MAX_WORD_LEN = 30
    letters = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й', 
            'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 
            'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ь', 'ю', 'я',]
    
    @staticmethod
    def weights(word):
        return [(Word.letters.index(alpha)+1)/10 if alpha in Word.letters else 0. for alpha in word ]
    @staticmethod
    def bin_position(index:int)->list:
        return [int(bit) for bit in bin(index)[2:]]
    @staticmethod
    def alpha_code(code:list):
        point_10 = 0.
        exp = 2
        for bit in code:
            point_10 += bit/(10**exp)
            exp+=1
        point_10 += 1/(10**exp)
        return point_10
    @staticmethod
    def word_code(word:str):
        alpha_nums = Word.weights(word)
        for i in range(len(alpha_nums)):
            position = Word.bin_position(i)
            if alpha_nums[i] == 0.: 
                print('zero')
                continue
            alpha_nums[i] += Word.alpha_code(position)
        return alpha_nums