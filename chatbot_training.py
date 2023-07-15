#pip install chatterbot
#pip install spacy
#python -m spacy download en

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# Create object of ChatBot class with Storage Adapter
bot = ChatBot(
    'Medibot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///database.sqlite3',
)

trainer = ListTrainer(bot)

trainer.train(['Hi','Hello, I am Medibot. I can help you by asking some questions. Shall we proceed?'])
trainer.train(['Hello','Hello, I am Medibot. I can help you by asking some questions. Shall we proceed?'])
trainer.train(['I need help','I can help you by asking some questions. Shall we proceed?'])
trainer.train(['Ok Thanks','Let\'s start'])
trainer.train(['Yes','Let\'s start'])
trainer.train(['Sure','Let\'s start'])
trainer.train(['No','No Problem! Have a Good Day!'])
trainer.train(['No Thanks','No Problem! Have a Good Day!'])
trainer.train(['Bye','Have a Good Day! Bye'])
trainer.train(['Who are you?','I am Medibot, a bot'])
trainer.train(['Are you alive?','Yes I am, and I can help you in medical diagnosis'])
