import axios from 'axios';

// Configured via frontend/.env (see frontend/.env.example). CRA bakes these in at build time.
const CHAT_API_URL =
  process.env.REACT_APP_CHAT_API_URL || 'http://localhost:3000/chat';
const PDF_API_URL =
  process.env.REACT_APP_PDF_API_URL || 'http://localhost:82/fill_pdf';

export async function chartAPI(payload: any) {
  try {
    let data = JSON.stringify(payload);

    let config = {
      method: 'post',
      maxBodyLength: Infinity,
      url: CHAT_API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      data: data,
    };

    const response = await axios.request(config);
    return response.data;
  } catch (error) {
    throw error;
  }
}


export async function sendMail(payload: any) {
  try {
    let data = JSON.stringify(payload);

    let config = {
      method: 'post',
      maxBodyLength: Infinity,
      url: PDF_API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      data: data,
    };

    const response = await axios.request(config);
    return response.data;
  } catch (error) {
    throw error;
  }
}

