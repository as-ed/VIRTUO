function scan(listen = false, book = null) {
	fetch("system/scan/start?listen=" + listen + ((book == null) ? "" : "&book=" + book), {method: "POST"})
		.then((response) => {
			if (response.ok) {
				if (listen) {
					document.getElementById("scan-listen").classList.add("inactive")
					document.getElementById("scan-only").classList.remove("inactive")
					for (let elem of document.getElementById("playback-controls").children)
						elem.classList.remove("inactive")
				} else {
					document.getElementById("scan-listen").classList.remove("inactive")
					document.getElementById("scan-only").classList.add("inactive")
					for (let elem of document.getElementById("playback-controls").children)
						elem.classList.add("inactive")
				}

				document.getElementById("stop-scan").classList.remove("inactive")
				for (let elem of document.getElementsByClassName("continue-scan"))
					elem.classList.add("inactive")

				const status = document.getElementById("scan-status")
				status.classList.remove("status-idle")
				status.classList.add("status-active")
				status.innerText = "Scanning in progress ..."

				return response.json()
			} else {
				return Promise.reject()
			}
		})
		.then((book) => {
			if (book == null) {
				document.getElementById("books").prepend(`
					<tr id="{book.id}">
						<td><input type="text" class="metadata" id="title_{book.id}" value="" placeholder="Enter title" oninput="setTitle('{book.id}', this, false)"></td>
						<td><input type="text" class="metadata" id="author_{book.id}" value="" placeholder="Enter author" oninput="setAuthor('{book.id}', this, false)"></td>
						<td>0</td>
						<td>{book.time}</td>
						<td><a href="books/{book.id}/book.txt" target="_blank" download>Text</a></td>
						<td><a href="books/{book.id}/book.pdf" target="_blank">PDF</a></td>
						<td><a href="books/{book.id}/book.epub" target="_blank">EPUB</a></td>
						<td><a href="books/{book.id}/book.mp3" target="_blank" download>MP3</a></td>
						<td><audio class="book-playback" controls preload="none" src="books/{book.id}/book.mp3"></audio></td>
						<td class="status_{book.id}"><span class="current-scan">Currently being scanned</span></td>
					</tr>`)
			} else {
				for (let elem of document.getElementsByClassName("status_" + book.id))
					elem.innerHTML = '<span class="current-scan">Currently being scanned</span>'
			}
		})
		.catch(() => alert("An error has occurred. Could not start scanning."))
}

function stopScan() {
	fetch("system/scan/stop", {method: "POST"})
}

function setVolume(){
	fetch("/system/setVolume/" + document.getElementById("volume").value, {method: "POST"})
}

function togglePause(){
	fetch("/system/togglePause", {method: "POST"})
		.then((response) => response.text())
		.then((text) => {
			document.getElementById("playpause").innerHTML = (text === "False") ? '<i class="fa-solid fa-play"  style="color: #DB504A"></i>' : '<i class="fa-solid fa-pause"  style="color: #DB504A"></i>'
		})
}

function setVoice(){
	const voice = document.getElementById("voiceSelect").value
	document.getElementById("voice-sample").src = "system/voiceSample/" + voice
	fetch("/system/setVoice/" + voice, {method: "POST"})
}

function fastForward() {
	fetch("system/fastForward", {method: "POST"})
}

function rewind() {
	fetch("system/rewind", {method: "POST"})
}

function setTitle(book, elem) {
	fetch(`books/${book}/title?title=${elem.value}`, {method: "POST"})
}

function setAuthor(book, elem) {
	fetch(`books/${book}/author?author=${elem.value}`, {method: "POST"})
}
