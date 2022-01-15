# Desafio-Space-Flight-News
Consumo da API [Space Flight News](https://api.spaceflightnewsapi.net/v3/documentation), realizando o CRUD de articles e relatório.

Métodos e tecnologias utilizadas:
  - Python
  - FastAPI
  - PostgreSQL
  - Heroku
  - SQLAlchemy 


# Como instalar o projeto:
  
  - Faça o clone do projeto.
  - Dentro da pasta de projeto, crie uma virtualenv com https://virtualenv.pypa.io/en/latest/:
     - ```
        virtualenv -p python3 nome_da_virtualenv ou virtualenv nome_da_virtualenv
        ```
  - Ative a virtualenv com:
     - Windows:
      -  ```
         nome_da_virtualenv/Scripts/Activate 
           ```
     - Linux ou macOS:
      - ```
         source nome_da_virtualenv/bin/activate
        ```
  - Faça instalação dos pacotes:
    - ```
      pip install -r requirements.txt
      ```
  - Execute o comando rodar o projeto:
    - ```
      uvicorn main:app --reload
      ```
   
https://desafio-space-flights.herokuapp.com/


This is a challenge by [Coodesh](https://coodesh.com)

Link da apresentação: https://www.loom.com/share/73f70df2d16d47bda7805147aeba6e88
