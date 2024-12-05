import os
from dotenv import load_dotenv
import streamlit as st
import mysql.connector
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS

# Configure Google Gemini API
load_dotenv()  # Load environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Mock database schema and descriptions
schema_descriptions = [
    "Table: sales_table, Column: ORDERNUMBER, Description: Unique identifier for sales order",
    "Table: sales_table, Column: QUANTITYORDERED, Description: Number of  quantity of products sold in units",
    "Table: sales_table, Column: SALES, Description: Amount of sales or revenue in USD",
    "Table: sales_table, Column: PRODUCTLINE, Description: Line of products",
    "Table: sales_table, Column: ORDERDATE, Description: Date of the order",
    "Table: sales_table, Column: YEAR_ID, Description: Year of the order",
    "Table: sales_table, Column: COUNTRY, Description: Country where the order was placed",
    "Table: sales_table, Column: CUSTOMERNAME, Description: Name of the customer who placed the order",
]

def generate_vector_index(text_segments):
    """
    Creates a vector store of text chunks and saves it to a FAISS index.

    Args:
        text_segments (list): List of text chunks to be embedded and indexed.

    Returns:
        None: The FAISS index is saved locally as 'faiss_index_store'.
    """
    embed_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_db = FAISS.from_texts(text_segments, embedding=embed_model)
    vector_db.save_local("faiss_index_store")
    return vector_db

vector_db = generate_vector_index(schema_descriptions)

# Utility Functions
def configure_streamlit():
    """Configure the Streamlit app settings."""
    st.set_page_config(page_title="Chat with your database through Gemini and RAG")
    st.header("Chat with your database through Gemini and RAG")


def get_gemini_response(question, prompt):
    """Get response from the Google Gemini model."""
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([prompt, question])
        return response.text
    except Exception as e:
        st.error(f"Error with Google Gemini API: {e}")
        return None


def connect_to_database():
    """Connect to the database using credentials from Streamlit session state."""
    try:
        connection = mysql.connector.connect(
            host=st.session_state["Host"],
            user=st.session_state["User"],
            password=st.session_state["Password"],
            database=st.session_state["Database"]
        )
        st.success(f"Connected to the database {st.session_state['Database']} successfully!")
        return connection
    except mysql.connector.Error as err:
        st.error(f"Database connection failed: {err}")
        return None


def read_sql_query(query):
    """Execute an SQL query and return the result."""
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        except mysql.connector.Error as err:
            st.error(f"Error executing query: {err}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None


# Prompt Definitions
PROMPT_QUERY = """
    You are an expert in converting English questions to MySQL query!
    Example SQL command: SELECT COUNT(*) FROM sales;

    The output should not include ``` or the word "sql".
"""

PROMPT_HUMANE_RESPONSE_TEMPLATE = """
    You are a customer service agent.

    Previously, you were asked: "{question}"
    The query result from the database is: "{result}".

    Please respond to the customer in a humane and friendly and detailed manner.
    For example, if the question is "What is the biggest sales of product A?", 
    you should answer "The biggest sales of product A is 1000 USD".
"""

# Define functions
def retrieve_schema(user_query):
    """Retrieve relevant schema details from vector store."""
    return vector_db.similarity_search(user_query, k=5)

def generate_sql_query(question, retrieved_schema):
    """Generate SQL query based on user query and retrieved schema using Gemini."""
    prompt = f"""
    
    You are an expert in converting English questions to MySQL query!
    Example SQL command: SELECT COUNT(*) FROM sales;

    The output should not include ``` or the word "sql".
    
    Based on the following database schema:
    {retrieved_schema}
    
    """
    return get_gemini_response(question, prompt)




# Main Application Logic
def main():
    show_query = True # Show query for debugging
    configure_streamlit()
    # User input

    question = st.text_input("Input: ", key="input")

    if st.button("Ask the question") and question:
        with st.spinner("Processing your query..."):
            schema_docs = retrieve_schema(question)
            retrieved_schema = "\n".join([doc.page_content for doc in schema_docs])

            st.subheader("Retrieved Schema Details")
            st.write(retrieved_schema)
            # Get SQL query from Gemini
            sql_query = generate_sql_query(question, retrieved_schema)

            if sql_query:
                if show_query:
                    st.subheader("Generated SQL Query:")
                    st.write(sql_query)

                # Execute the SQL query
                result = read_sql_query(sql_query)
                if result:
                    if show_query:
                        st.subheader("Query Results:")
                        for row in result:
                            st.write(row)

                    # Generate humane response
                    humane_response = get_gemini_response(
                        question, PROMPT_HUMANE_RESPONSE_TEMPLATE.format(question=question, result=result)
                    )
                    st.subheader("AI Response:")
                    st.write(humane_response)
                else:
                    st.error("No results returned from the query.")

    # Sidebar for Database Configuration
    with st.sidebar:
        st.subheader("Database Settings")
        st.text_input("Host", value="localhost", key="Host")
        st.text_input("Port", value="3306", key="Port")
        st.text_input("User", value="root", key="User")
        st.text_input("Password", type="password", value="", key="Password")
        st.text_input("Database", value="sales_database", key="Database")
        if st.button("Test Connection"):
            with st.spinner("Testing database connection..."):
                if connect_to_database():
                    st.success("Connection successful!")

    # Footer
    st.markdown(
        """
        <style>
        .footer {position: fixed;left: 0;bottom: 0;width: 100%;background-color: #000;color: white;text-align: center;}
        </style>
        <div class='footer'>
            <p>ardyadipta@gmail.com</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Run the app
if __name__ == "__main__":
    main()
