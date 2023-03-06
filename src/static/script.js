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
			document.getElementById("volume").value = text * 100
		})
}

function setVolume(){
	fetch('/system/setVolume/' + document.getElementById("volume").value, {method: 'POST'})
}

function togglePause(){
	fetch('/system/togglePause', {method: 'POST'})
		.then((response) => response.text())
		.then((text) => {
			document.getElementById("playpause").innerHTML = (text === "False") ? "<i class='fa-solid fa-play'  style='color: #DB504A'></i>" : "<i class='fa-solid fa-pause'  style='color: #DB504A'></i>"
		})
}

function setVoice(){
	fetch('/system/setVoice/' + document.getElementById("voiceSelect").value, {method: 'POST'})
}

function fastForward() {
	fetch('system/fastForward', {method: 'POST'})
}

function rewind() {
	fetch('system/rewind', {method: 'POST'})
}

function setTitle(book, elem) {
	fetch(`books/${book}/title?title=${elem.value}`, {method: "POST"})
}

function setAuthor(book, elem) {
	fetch(`books/${book}/author?author=${elem.value}`, {method: "POST"})
}
