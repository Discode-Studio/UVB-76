// Localiser l'élément audio sur la page
const audioElement = document.querySelector('audio');

// Créer un contexte audio pour capturer l'audio
const audioContext = new AudioContext();
const source = audioContext.createMediaElementSource(audioElement);
const destination = audioContext.createMediaStreamDestination();

// Connecter la source audio à la destination et à la sortie audio par défaut
source.connect(destination);
source.connect(audioContext.destination);

// Le flux audio est maintenant dans 'destination.stream'
// Vous pouvez utiliser ce flux pour le diffuser via WebRTC, WebSocket, ou le sauvegarder
