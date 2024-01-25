# -*- coding: utf-8 -*-

import os
from flask import Flask, request, session, redirect, jsonify, url_for, render_template
from flask_cors import CORS
import requests
import json
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "new_credentials.json"


# SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SAMPLE_SPREADSHEET_ID = '1MmGXm6QSLwK-YP6bEVKWKRDexq4ofUXc-cQXS4vLNXQ'
# csvFilePath = './places_results.csv'
newSheetName = "Circulator Pump Replacement W912WJ24Q0031"  # Please set the new sheet name.




# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v2'

app = Flask(__name__)
CORS(app, origins=["http://localhost:8080", "http://localhost:3000"])
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = '7d6059e8ad65811de5013da1f3f246f1e6979949c6eb89a75165c32d60be3bde'


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/test')
def test_api_request():
  if 'credentials' not in session:
    return redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **session['credentials'])
  service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)

# ID of the spreadsheet to add a sheet to
  spreadsheet_id = '1MmGXm6QSLwK-YP6bEVKWKRDexq4ofUXc-cQXS4vLNXQ'
  response = requests.post(url, json=data, headers=headers)

  if response.status_code == 200:
     results = response.json().get("places")

     extracted_data = []
     for item in results:
       extracted_item = [
        item["displayName"]["text"],
          item["nationalPhoneNumber"],
          "",
          "",
         item["formattedAddress"],
         item.get("websiteUri")  # Use .get() to handle potential missing keys
       ]
       extracted_data.append(extracted_item)
     print(extracted_data)
    

     headers = ["Name", "Phone Number", "Email", "Notes", "Info", "Address", "Website"]

     request_body = {"values": extracted_data}

#      print(request_body)


# Append headers as the first row
  responseheader = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range='New Sheet Name!A1',
        body={"values": [headers]},
        valueInputOption='USER_ENTERED'
    ).execute()
  

# Extract values for a single row
#   row_values = [data["name"], data["age"], data["city"]]

#   request_body = {"values": [row_values]}

  responsevalues = service.spreadsheets().values().append(
    spreadsheetId=spreadsheet_id,
    range='New Sheet Name!A2',  # Adjust sheet name and range as needed
    body=request_body,
    valueInputOption='USER_ENTERED'
).execute()
#Create a new sheet with the specified title
  


  print('New sheet created!')
  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  session['credentials'] = credentials_to_dict(credentials)

  return jsonify('New sheet created!')


@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  session['state'] = state
  print(authorization_url)

  return redirect(authorization_url), 301


@app.route('/oauth2callback')
def oauth2callback():
  print("i am waleed.")
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  session['credentials'] = credentials_to_dict(credentials)

  return redirect('/') 


@app.route('/revoke')
def revoke():
  if 'credentials' not in session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **session['credentials'])

  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
  if 'credentials' in session:
    del session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())


@app.route('/create_sheet', methods=['POST'])
def create_sheet():
   if 'credentials' not in session:
    return redirect('authorize')
  # Load credentials from the session.
   credentials = google.oauth2.credentials.Credentials(
    **session['credentials'])
   service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)
  # Access the argument from the request
  # print(request.get_json())
  # Alternatively, use:

   title = request.form['sheet_name']
   
   spreadsheet_id = '1MmGXm6QSLwK-YP6bEVKWKRDexq4ofUXc-cQXS4vLNXQ'
   request_body = {
        'requests': [
            {
                'addSheet': {
                    'properties': {
                        'title': title
                    }
                }
            }
        ]
    }
   try: 
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=request_body
    ).execute()
    print('Batch update successful!')
  # except HttpError as err:
  #       print('An error occurred: %s' % err)
  #       return flask.jsonify('An error occurred:')
        # Consider logging the error for further analysis
        # You might also want to implement specific actions based on the error code
   except Exception as err:
        print('An unexpected error occurred: %s' % err)
        return jsonify('A sheet with the name,' + title +' already exists')

        # Handle other potential errors gracefully
  # Return a response
   return "Argument processed successfully!"


@app.route('/add_business', methods=['POST'])
def add_business():
   print("waleed")
   if 'credentials' not in session:
    return redirect('authorize')
  # Load credentials from the session.
   credentials = google.oauth2.credentials.Credentials(
    **session['credentials'])
   service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)
  # Access the argument from the request
  # print(request.get_json())
  #  argument_value = request.get_json() 
   spreadsheet_id = 'Y_h7XcUvm9scOJPNhdZ3eaLvrt6aciYt6sCZkGLj6EQ'
   request_body = {
        'requests': [
            {
                'addSheet': {
                    'properties': {
                        'title': request.form['sheet_name']
                    }
                }
            }
        ]
    }
   try: 
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=request_body
    ).execute()
    print('Batch update successful!')
    
   except Exception as err:
        print('An unexpected error occurred: %s' % err)
        return jsonify('A sheet with the name,' + request.form['sheet_name'] +' already exists')

        # Handle other potential errors gracefully
  # Return a response
   url = 'https://places.googleapis.com/v1/places:searchText'
   headers = {
    'Content-Type': 'application/json',
    'X-Goog-Api-Key': 'AIzaSyAMHLXy_sP6O2Tc10eySjedDFdYWQDyuCI',
    'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri'
       }

   data = {
    "textQuery": request.form['query'],
    "rankPreference": "RELEVANCE"
     }
   response = requests.post(url, json=data, headers=headers)

   if response.status_code == 200:
     results = response.json().get("places")

     extracted_data = []
     for item in results:
       extracted_item = [
        item["displayName"]["text"],
          item["nationalPhoneNumber"],
          "",
          "",
         item["formattedAddress"],
         item.get("websiteUri")  # Use .get() to handle potential missing keys
       ]
       extracted_data.append(extracted_item)
  #  print(extracted_data) 
    # Get from URL query parameters
   table_headers = ["Name", "Phone Number", "Email", "Notes", "Info", "Address", "Website"]

   responseheader = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=request.form['sheet_name']+'!A1',
        body={"values": [table_headers]},
        valueInputOption='USER_ENTERED'
    ).execute()
  # Process the argument value as needed
   request_body = {"values": extracted_data}
   print(request_body)
   responsevalues = service.spreadsheets().values().append(
    spreadsheetId=spreadsheet_id,
    range=request.form['sheet_name']+'!A2',  # Adjust sheet name and range as needed
    body=request_body,
    valueInputOption='USER_ENTERED'
    ).execute() 
   
   session['credentials'] = credentials_to_dict(credentials)

   return request.form['sheet_name']+ ' updated!'
   

def credentials_to_dict(credentials):

  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')


if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    # os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))