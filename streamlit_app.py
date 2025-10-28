# Import python packages
import streamlit as st
import requests
import time
import pandas as pd

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
                # st.write(f"DEBUG Conversation ID: {conversation_id}")
                # st.write(f"DEBUG Message ID: {message_id}")

                # Poll for completion
                status_endpoint = f"https://{databricks_host}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}"
                status = "NEW"
                max_retries = 30
                retries = 0
                result = None
                with st.status("Working... (click for detailed status)") as status_st:
                    while status != "COMPLETED" and retries < max_retries:
                        status_resp = requests.get(status_endpoint, headers=headers)
                        status_resp.raise_for_status()
                        status_json = status_resp.json()
                        status = status_json.get("status", "IN_PROGRESS").replace("_", " ").title()
                        if status != "Completed":
                            status_st.update(label=f"{status}...")
                            time.sleep(2)
                            retries += 1
                        else:
                            status_st.update(label="Completed!", state="complete")

                if status == "COMPLETED":
                    for att in status_json.get("attachments", []):
                        attachment_id = att.get("attachment_id", "")
                        response_endpoint = f"https://{databricks_host}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}/attachments/{attachment_id}/query-result"
                        response_resp = requests.get(response_endpoint, headers=headers)
                        response_resp.raise_for_status()
                        response_json = response_resp.json()

                        # Visualize the results in a table
                        statement_response = response_json.get("statement_response", {})
                        result = statement_response.get("result", {})
                        manifest = statement_response.get("manifest", {})
                        columns = [col["name"] for col in manifest.get("schema", {}).get("columns", [])]
                        data = result.get("data_array", [])
                        if columns and data:
                            df = pd.DataFrame(data, columns=columns)
                            st.dataframe(df)
                        else:
                            st.write(response_json)

                else:
                    st.warning("Genie AI response did not complete in time.")

            else:
                st.warning("No conversation_id returned from Genie AI.")
        except Exception as e:
            st.error(f"Error communicating with Databricks Genie AI: {e}")
    else:
        st.warning("Please enter a prompt before submitting.")
