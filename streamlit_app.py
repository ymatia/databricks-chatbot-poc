# Import python packages
import streamlit as st
import requests

databricks_host = "adb-3563412912731739.19.azuredatabricks.net"
space_id = "01f09ea26052149da9728e72836c8245"
endpoint = f"https://{databricks_host}/api/2.0/genie/spaces/{space_id}/start-conversation"

# Write directly to the app
st.title(f"Databricks Genie AI")
st.write("Enter a prompt to get started:")
api_key = st.text_input('API Key:')
prompt = st.text_input('Prompt:')

if st.button('Submit'):
    if prompt:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "content": prompt
        }

        try:
            response = requests.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            st.write("Genie AI Response:")
            st.write(result.get("response", "No response field in result."))
        except Exception as e:
            st.error(f"Error communicating with Databricks Genie AI: {e}")
    else:
        st.warning("Please enter a prompt before submitting.")
