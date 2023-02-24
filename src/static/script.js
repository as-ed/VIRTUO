function startScan() {
  fetch('system/scan/start', {method: 'POST'})
}

function stopScan() {
  fetch('system/scan/stop', {method: 'POST'})
}

function getVolume(){
  fetch(
    '/system/getVolume', {method:'GET'})
    .then((response) => response.text())
    .then((text) => {
      document.getElementById("volume").value = text
    })
}

function setVolume(){
  fetch('/system/setVolume/' + document.getElementById("volume").value, {method: 'POST'})
}

function togglePause(){
  fetch('/system/togglePause', {method: 'POST'})
  .then((response) => response.text())
  .then((text) => {
    let playpause = (text === "False") ? "Play":"Pause";
    document.getElementById("playpause").innerHTML = playpause
  })
}

function setVoice(){
  fetch('/system/setVoice/' + document.getElementById("voiceSelect").value, {method: 'POST'})
}

function fastforward() {
  fetch('system/fast-forward', {method: 'POST'})
}

function rewind() {
  fetch('system/rewind', {method: 'POST'})
}

