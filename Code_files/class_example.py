#! usr/bin/python

#Mediator class example:

from time import sleep

VOWELS = "aeiou"

class Chat:
    
    def __init__(self):
        self.chat_log = []
      
    def connect_human(self, human):
        human.chat = self
    
    def connect_robot(self, robot):
        robot.chat = self
    
    def translate_to_binary(self, text: str) -> str:
        return "".join(["0" if char in VOWELS else "1" for char in text])
        
    def show_human_dialogue(self): 
        return '\n'.join(person + text for person, text in self.chat_log)
        
    def show_robot_dialogue(self):
        return '\n'.join(person + self.translate_to_binary(text) for person, text in self.chat_log)

class Human:
    
    def __init__(self, name: str):
        self.name = name
        
    def send(self, text: str) -> list:
        self.chat.chat_log.append( [''.join([self.name, ' said: ']), text] )

class Robot:
    
    def __init__(self, bot_name: str):
        self.bot_name = bot_name
        
    def send(self, text: str) -> list:
        self.chat.chat_log.append( [''.join([self.bot_name, ' said: ']), text] )


if __name__ == '__main__':

    chat = Chat()
    karl = Human("Karl")
    bot = Robot("R2D2")
    chat.connect_human(karl)
    chat.connect_robot(bot)
    karl.send("Hi! What's new?")
    bot.send("Hello, human. Could we speak later about it?")
    assert chat.show_human_dialogue() == "Karl said: Hi! What's new?\nR2D2 said: Hello, human. Could we speak later about it?"
    assert chat.show_robot_dialogue() == "Karl said: 101111011111011\nR2D2 said: 10110111010111100111101110011101011010011011"
    print("Human text:\n" + chat.show_human_dialogue()+'\n', 'Robot code:\n'+chat.show_robot_dialogue()+'\n')
    print("Tests are done!")
    sleep(10)