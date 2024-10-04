const puppeteer = require('puppeteer');

// Fonction pour capturer l'audio depuis un AudioWorklet
async function captureAudioFromWebSDR() {
  const browser = await puppeteer.launch({
    headless: true,  // Mode headless activé
    args: ['--no-sandbox', '--disable-setuid-sandbox']  // Ajout d'arguments pour une meilleure compatibilité
  });
  
  const page = await browser.newPage();

  // Aller à la page WebSDR
  await page.goto('http://websdr.ewi.utwente.nl:8901/', { waitUntil: 'domcontentloaded' });

  // Injecter le code pour intercepter l'audio
  await page.evaluate(() => {
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
        console.log("Audio stream captured:", stream);
      });
    } else {
      console.log('AudioContext or AudioWorklet not supported.');
    }
  });

  console.log("Audio capture attempt complete.");

  await browser.close();
}

captureAudioFromWebSDR();
