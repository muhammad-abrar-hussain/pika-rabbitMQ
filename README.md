`Qtip_app
├── Qtip_fapi
│   ├── assets
│   ├── routers
│   │   ├── __init__.py
│   │   ├── knowledgebase.py
│   │   └── Question.py
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── receiver.py
│   └── textExtract.py
│
├── rabbitMQ 
│   ├── Question.py
│   └── Start_learning.py
├── RMQ_env
├── img.png
└── README.md
`

Start application: uvicorn Qtip_fapi.main:app --reload --port 8000


**About Folders:**
rabbitMQ: Present queue initializers & add message into Queue as sender.
RMQ_env: Present virtual environment setup


**About files:**
textExtract.py: Present functions to extract text from different kind of files.
receiver.py: Setup RabbitMQ consumer and made API calls to get and post data.
main.py: Startup file to start application/fastapi.
database.py: Made connection with db in file.
knowledgebase.py: Present get and post API's for start_learning_Queue
Question.py: Present get and put API's for Question_Queue.





