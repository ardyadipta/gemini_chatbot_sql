import os
from dotenv import load_dotenv
import streamlit as st
import mysql.connector
import google.generativeai as genai

# Configure Google Gemini API
load_dotenv()  # Load environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Utility Functions
def configure_streamlit():
    """Configure the Streamlit app settings."""
    st.set_page_config(page_title="Chat with your database through Gemini")
    st.header("Chat with your database through Gemini")


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

    The SQL database "sales_database" has the table "sales_table" and the following columns:
    - ORDERNUMBER: Unique identifier for sales
    - QUANTITYORDERED: Number of products sold
    - SALES: Amount of sales or revenue in USD
    - PRODUCTLINE: Line of products
    - ORDERDATE: Date of order
    - YEAR_ID: Year of the order
    - COUNTRY: Country
    - CUSTOMERNAME: Name of customer

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

# Be careful and don't sugarcoat the number. Whether the number is rising or declining, tell the customer as it is.
#

# Main Application Logic
def main():
    show_query = False # Show query for debugging
    configure_streamlit()

    # User input
    question = st.text_input("Input: ", key="input")
    if st.button("Ask the question") and question:
        with st.spinner("Processing your query..."):
            # Get SQL query from Gemini
            sql_query = get_gemini_response(question, PROMPT_QUERY)
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
