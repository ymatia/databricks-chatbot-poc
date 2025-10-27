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

                # Poll for completion
                status_endpoint = f"https://{databricks_host}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}"
                status = "NEW"
                max_retries = 30
                retries = 0
                result = None
                while status != "COMPLETED" and retries < max_retries:
                    status_resp = requests.get(status_endpoint, headers=headers)
                    status_resp.raise_for_status()
                    status_json = status_resp.json()
                    status = status_json.get("status", "IN_PROGRESS")
                    if status != "COMPLETED":
                        st.write(f"Status: {status}. Waiting for completion...")
                        time.sleep(2)
                        retries += 1

                if status == "COMPLETED":
                    st.write("Genie AI Response:")
                    for att in status_json.get("attachments", []):
                        attachment_id = att.get("attachment_id", "")
                        response_endpoint = f"https://{databricks_host}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}/attachments/{attachment_id}/query-result"
                        response_resp = requests.get(response_endpoint, headers=headers)
                        response_resp.raise_for_status()
                        response_json = response_resp.json()
                        st.write(response_json)
                else:
                    st.warning("Genie AI response did not complete in time.")

            else:
                st.warning("No conversation_id returned from Genie AI.")
        except Exception as e:
            st.error(f"Error communicating with Databricks Genie AI: {e}")
    else:
        st.warning("Please enter a prompt before submitting.")
