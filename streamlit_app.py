# Import python packages
import streamlit as st
import requests
import time

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
            conversation_id = result.get("conversation_id", "")
            message_id = result.get("message_id", "")
            if conversation_id:
                st.write(f"DEBUG Conversation ID: {conversation_id}")
                st.write(f"DEBUG Message ID: {message_id}")

                list_messages_endpoint = f"https://{databricks_host}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages"
                list_messages_resp = requests.get(list_messages_endpoint, headers=headers)
                list_messages_resp.raise_for_status()
                list_messages_json = list_messages_resp.json()
                st.write("Messages in Conversation:")
                st.write(list_messages_json)
                for message in list_messages_json.get("messages", []):
                    st.write(message)

            else:
                st.warning("No conversation_id returned from Genie AI.")
        except Exception as e:
            st.error(f"Error communicating with Databricks Genie AI: {e}")
    else:
        st.warning("Please enter a prompt before submitting.")
