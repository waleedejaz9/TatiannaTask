require('dotenv').config();
const express = require('express');
const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
const port = process.env.PORT || 5000;

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
  if (!oAuth2Client) {
      return res.redirect('/authorize');
  }

  const sheetName = req.body.sheet_name;
  const query = req.body.query;
  const url = `https://places.googleapis.com/v1/places:searchText?query=${encodeURIComponent(query)}&key=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`;
  console.log(url)
  try {
      // Fetch data from Google Places API
      const response = await fetch(url);
      const data = await response.json();
      
      if (!data || !data.places) {
          throw new Error('Failed to retrieve data from Google Places API');
      }

      const extractedData = data.places.map(item => ([
          item.displayName.text,
          item.nationalPhoneNumber || '',
          '', // Placeholder for Email
          '', // Placeholder for Notes
          item.formattedAddress || '',
          item.websiteUri || ''
      ]));

      const sheets = google.sheets({ version: 'v4', auth: oAuth2Client });

      // Add a new sheet
      await sheets.spreadsheets.batchUpdate({
          spreadsheetId,
          requestBody: {
              requests: [{
                  addSheet: {
                      properties: {
                          title: sheetName
                      }
                  }
              }]
          }
      });

      // Prepare headers
      const headers = ["Name", "Phone Number", "Email", "Notes", "Address", "Website"];
      // Append the headers
      await sheets.spreadsheets.values.append({
          spreadsheetId,
          range: `${sheetName}!A1`,
          valueInputOption: 'USER_ENTERED',
          requestBody: { values: [headers] }
      });

      // Append the extracted data
      await sheets.spreadsheets.values.append({
          spreadsheetId,
          range: `${sheetName}!A2`,
          valueInputOption: 'USER_ENTERED',
          requestBody: { values: extractedData }
      });

      res.send(`${sheetName} updated successfully!`);
  } catch (error) {
      console.error('An error occurred:', error);
      res.status(500).send('An error occurred while processing your request.');
  }
});

app.listen(port, () => {
  console.log(`App listening at http://localhost:${port}`);
});
