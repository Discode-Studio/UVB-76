const puppeteer = require('puppeteer');

// Fonction pour accéder à la page WebSDR et capturer l'audio
async function captureAudio() {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Aller à la page WebSDR
  await page.goto('http://websdr.ewi.utwente.nl:8901/', { waitUntil: 'domcontentloaded' });

  // Attendre que l'élément audio soit présent
  const audioHandle = await page.$('audio');

  if (audioHandle) {
    // Injecter du code dans le contexte du navigateur pour capturer l'audio
    await page.evaluate(() => {
      const audioElement = document.querySelector('audio');
      const audioContext = new AudioContext();
      const source = audioContext.createMediaElementSource(audioElement);
      const destination = audioContext.createMediaStreamDestination();

      source.connect(destination);
      source.connect(audioContext.destination);

      // Retourner le flux audio
      return destination.stream;
    });
    
    console.log("Audio capture successful");
  } else {
    console.log("Audio element not found");
  }

  // Fermer le navigateur
  await browser.close();
}

captureAudio();
