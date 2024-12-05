# Chat with your database using Gemini Tutorial

This repo is for using Gemini to chat with your SQL database.
Inspired by https://github.com/leodeveloper/google-gemini-chat-with-sqlserver/

## Objective

* To demonstrate on how to build a chatbot using Gemini and RAG technique to query your database

In this instruction, I use pyenv for the virtual environment and python 3.9.17. It actually works on python >= 3.9

# Prepare Environment

    git clone https://github.com/ardyadipta/gemini_chatbot_sql
    cd gemini_chatbot_sql
    pyenv virtualenv 3.9.17 gemini_chatbot
    pyenv activate gemini_chatbot
    pip install -r requirements.txt

# Create API Key
* visit https://aistudio.google.com/prompts/new_chat?pli=1

        export GOOGLE_API_KEY=`<your Google API key`>
        echo $GOOGLE_API_KEY

## How to use this tutorial

### Setup your MySQL server on local

1. I assume you already have a MySQL server on locale, if not, download from [here](https://dev.mysql.com/downloads/mysql/) and follow the instruction to install.
2. Download the dataset from Kaggle [here](https://www.kaggle.com/datasets/kyanyoga/sample-sales-data?select=sales_data_sample.csv).
In my case, I saved it into /tmp/ so that it can be accessible to the MySQL server on my local.
3. Upload CSV to MySQL table 

```commandline
python upload_csv_to_sql_table.py
```

### Run app without RAG to see how it performs

``` streamlit run app.py```

### Run app with RAG

``` streamlit run app_with_rag.py```