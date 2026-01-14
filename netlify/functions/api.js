const { spawn } = require('child_process');
const { readFile } = require('fs').promises;
const { join } = require('path');

exports.handler = async (event, context) => {
  // Handle preflight requests
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE'
      },
      body: ''
    };
  }

  // Handle API requests
  try {
    const python = spawn('python', ['app.py', JSON.stringify(event)]);
    
    let result = '';
    let error = '';

    python.stdout.on('data', (data) => {
      result += data.toString();
    });

    python.stderr.on('data', (data) => {
      error += data.toString();
    });

    return new Promise((resolve) => {
      python.on('close', (code) => {
        if (code !== 0) {
          return resolve({
            statusCode: 500,
            body: JSON.stringify({ error: 'Server error', details: error })
          });
        }
        
        try {
          const response = JSON.parse(result);
          resolve({
            statusCode: 200,
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify(response)
          });
        } catch (e) {
          resolve({
            statusCode: 200,
            headers: {
              'Content-Type': 'text/html',
              'Access-Control-Allow-Origin': '*'
            },
            body: result
          });
        }
      });
    });
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
