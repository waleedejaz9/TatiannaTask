const express = require('express');
const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
const port = process.env.PORT || 8080;

// Setup for parsing application/json and urlencoded request bodies
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// If using views
app.set('view engine', 'ejs');

// Google Sheets setup
const CLIENT_SECRETS_FILE = path.join(__dirname, 'credentials.json');
const SCOPES = ['https://www.googleapis.com/auth/spreadsheets'];
const TOKEN_PATH = path.join(__dirname, 'token.json');

// Initialize OAuth2 client
let oAuth2Client;

// Load client secrets
fs.readFile(CLIENT_SECRETS_FILE, (err, content) => {
  if (err) return console.log('Error loading client secret file:', err);
  const credentials = JSON.parse(content);
  const { client_secret, client_id, redirect_uris } = credentials.web;
  oAuth2Client = new google.auth.OAuth2(client_id, client_secret, redirect_uris);

  // Check if we have previously stored a token.
  fs.readFile(TOKEN_PATH, (err, token) => {
    if (err) return getNewToken(oAuth2Client);
    oAuth2Client.setCredentials(JSON.parse(token));
  });
});

// Get new token after prompting for user authorization
function getNewToken(oAuth2Client, callback) {
  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
  });
  console.log('Authorize this app by visiting this url:', authUrl);
  // Redirect user to authUrl...
}

app.get('/', (req, res) => {
  res.render('index'); // or res.send('Hello World!');
});

app.get('/authorize', (req, res) => {
  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
  });
  res.redirect(authUrl);
});

app.get('/oauth2callback', async (req, res) => {
  const { code } = req.query;
  try {
    const { tokens } = await oAuth2Client.getToken(code);
    oAuth2Client.setCredentials(tokens);
    // Store the token to disk for later program executions
    fs.writeFile(TOKEN_PATH, JSON.stringify(tokens), (err) => {
      if (err) return console.error(err);
      console.log('Token stored to', TOKEN_PATH);
    });
    res.redirect('/');
  } catch (error) {
    console.error('Error retrieving access token', error);
    res.redirect('/authorize');
  }
});

// Additional routes for your application...
// Route to add business
app.post('/add_business', async (req, res) => {
  console.log("waleed");

  if (!req.session || !req.session.credentials) {
      return res.redirect('authorize');
  }

  // Initialize Google Sheets API
  const auth = new google.auth.GoogleAuth({
      credentials: req.session.credentials,
      scopes: ['https://www.googleapis.com/auth/spreadsheets']
  });

  const sheets = google.sheets({version: 'v4', auth});

  const spreadsheetId = 'Y_h7XcUvm9scOJPNhdZ3eaLvrt6aciYt6sCZkGLj6EQ';
  const sheetName = req.body.sheet_name; // Ensure you have body-parser setup to parse request.body

  const request_body = {
      requests: [
          {
              addSheet: {
                  properties: {
                      title: sheetName
                  }
              }
          }
      ]
  };

  try {
      const response = await sheets.spreadsheets.batchUpdate({
          spreadsheetId,
          resource: request_body,
      });
      console.log('Batch update successful!');
  } catch (err) {
      console.log('An unexpected error occurred: %s', err);
      return res.json(`A sheet with the name ${sheetName} already exists`);
  }

  // Fetching data from an external API
  const url = 'https://places.googleapis.com/v1/places:searchText';
  const headers = {
      'Content-Type': 'application/json',
      'X-Goog-Api-Key': "AIzaSyAMHLXy_sP6O2Tc10eySjedDFdYWQDyuCI", // Store your API key in .env file
  };

  const data = {
      "textQuery": req.body.query,
      "rankPreference": "RELEVANCE"
  };

  try {
      const response = await axios.post(url, data, {headers});
      if (response.status_code === 200) {
          const results = response.data.places;
          const extracted_data = results.map(item => [
              item.displayName.text,
              item.nationalPhoneNumber,
              "",
              "",
              item.formattedAddress,
              item.websiteUri || ""
          ]);

          // Append headers
          const table_headers = ["Name", "Phone Number", "Email", "Notes", "Info", "Address", "Website"];
          await sheets.spreadsheets.values.append({
              spreadsheetId,
              range: `${sheetName}!A1`,
              valueInputOption: 'USER_ENTERED',
              resource: {values: [table_headers]},
          });

          // Append data
          await sheets.spreadsheets.values.append({
              spreadsheetId,
              range: `${sheetName}!A2`,
              valueInputOption: 'USER_ENTERED',
              resource: {values: extracted_data},
          });

          console.log("Data appended successfully");
          req.session.credentials = auth.credentials; // Update session credentials
          res.send(`${sheetName} updated!`);
      } else {
          throw new Error('Failed to fetch places data');
      }
  } catch (error) {
      console.error('Error fetching places data:', error);
      res.status(500).send('Error fetching places data');
  }
});

app.post('/create_sheet', async (req, res) => {
  if (!req.session || !req.session.credentials) {
      return res.redirect('authorize');
  }

  // Initialize Google Sheets API
  const auth = new google.auth.GoogleAuth({
      credentials: req.session.credentials,
      scopes: ['https://www.googleapis.com/auth/spreadsheets']
  });

  const sheets = google.sheets({version: 'v4', auth});

  const spreadsheetId = '1MmGXm6QSLwK-YP6bEVKWKRDexq4ofUXc-cQXS4vLNXQ';
  const sheetName = req.body.sheet_name; // Ensure you have body-parser setup to parse request.body

  const request_body = {
      requests: [
          {
              addSheet: {
                  properties: {
                      title: sheetName
                  }
              }
          }
      ]
  };

  try {
      const response = await sheets.spreadsheets.batchUpdate({
          spreadsheetId,
          resource: request_body,
      });
      console.log('Batch update successful!');
      res.send("Argument processed successfully!");
  } catch (err) {
      console.log('An unexpected error occurred: %s', err);
      res.status(500).json(`A sheet with the name ${sheetName} already exists`);
  }
});

app.listen(port, () => {
  console.log(`App listening at http://localhost:${port}`);
});
