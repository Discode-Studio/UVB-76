const puppeteer = require('puppeteer');

// Fonction pour capturer l'audio depuis un AudioWorklet
async function captureAudioFromWebSDR() {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  // Aller à la page WebSDR
  await page.goto('http://websdr.ewi.utwente.nl:8901/', { waitUntil: 'domcontentloaded' });

  // Injecter le code pour intercepter l'audio
  await page.evaluate(() => {
    // Assurez-vous que l'AudioContext et l'AudioWorklet sont supportés
    if (typeof AudioContext !== 'undefined' && typeof AudioWorklet !== 'undefined') {
      const originalAudioContext = window.AudioContext || window.webkitAudioContext;
      const audioContext = new originalAudioContext();

      // Intercepter et rediriger le flux audio
      const destination = audioContext.createMediaStreamDestination();  // Destination du flux

      // Injecter le flux dans le travail de l'AudioWorklet
      audioContext.audioWorklet.addModule('websdr-sound.js').then(() => {
        const workletNode = new AudioWorkletNode(audioContext, 'sound-processor');
        workletNode.connect(destination); // Connecter à la destination

        // Option : Connecter à un WebSocket pour envoyer les données ailleurs
        // Ici, nous envoyons simplement le flux à la sortie audio
        workletNode.connect(audioContext.destination);

        // Maintenant, le flux est capturé dans `destination.stream`
        const stream = destination.stream;

        // Utilisez le stream comme vous le souhaitez (par exemple, envoyer à un serveur ou autre)
        console.log("Audio stream captured:", stream);
      });
    } else {
      console.log('AudioContext or AudioWorklet not supported.');
    }
  });

  console.log("Audio capture attempt complete.");

  // Ne fermez pas le navigateur tant que la capture n'est pas terminée
  await browser.close();
}

captureAudioFromWebSDR();
