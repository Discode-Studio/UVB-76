const puppeteer = require('puppeteer');
const axios = require('axios');

// Fonction pour capturer l'audio depuis un AudioWorklet et l'envoyer au serveur Flask
async function captureAudioFromWebSDR() {
  try {
    const browser = await puppeteer.launch({
      headless: true,  // Mode headless activé
      args: ['--no-sandbox', '--disable-setuid-sandbox']  // Ajout d'arguments pour une meilleure compatibilité
    });
    
    const page = await browser.newPage();

    // Aller à la page WebSDR
    await page.goto('http://websdr.ewi.utwente.nl:8901/', { waitUntil: 'domcontentloaded' });

    // Injecter le code pour intercepter l'audio
    const stream = await page.evaluate(() => {
      return new Promise((resolve, reject) => {
        if (typeof AudioContext !== 'undefined' && typeof AudioWorklet !== 'undefined') {
          const originalAudioContext = window.AudioContext || window.webkitAudioContext;
          const audioContext = new originalAudioContext();

          const destination = audioContext.createMediaStreamDestination();

          audioContext.audioWorklet.addModule('websdr-sound.js').then(() => {
            const workletNode = new AudioWorkletNode(audioContext, 'sound-processor');
            workletNode.connect(destination);  // Connecter à la destination

            // Connecter à la sortie audio
            workletNode.connect(audioContext.destination);

            const stream = destination.stream;
            resolve(stream);
          }).catch(reject);
        } else {
          reject(new Error('AudioContext or AudioWorklet not supported.'));
        }
      });
    });

    if (stream) {
      // Envoi du stream audio au serveur Flask
      const response = await axios.post('http://127.0.0.1:5000/upload-audio', stream, {
        headers: {
          'Content-Type': 'audio/webm'  // Format à définir selon la capture
        }
      });

      console.log("Audio stream sent to server, response:", response.data);
    } else {
      console.log('Failed to capture audio stream.');
    }

    await browser.close();
  } catch (error) {
    console.error("An error occurred:", error.message);
  }
}

captureAudioFromWebSDR();
