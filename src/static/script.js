function scan(listen = false, book = null) {
	fetch("system/scan/start?listen=" + listen + ((book == null) ? "" : "&book=" + book), {method: "POST"})
		.then((response) => {
			if (response.ok) {
				if (listen) {
					document.getElementById("scan-listen").classList.add("inactive")
					document.getElementById("scan-only").classList.remove("inactive")
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
		.then((new_book) => {
			if (document.getElementById(new_book.id) == null) {
				const elem = document.createElement("tr")
				elem.id = new_book.id
				elem.classList.add("book")
				elem.innerHTML = `
					<tr id="${new_book.id}" class="book">
						<td class="md-row sm-row"><input type="text" class="metadata" id="title_${new_book.id}" value="" placeholder="Enter title" oninput="setTitle('${new_book.id}', this)"></td>
						<td class="md-row sm-row"><input type="text" class="metadata" id="author_${new_book.id}" value="" placeholder="Enter author" oninput="setAuthor('${new_book.id}', this)"></td>
						<td id="pages_${new_book.id}" class="md-row sm-row"><span class="mobile-bold">0</span><span class="mobile-only"> pages, scanned at </span></td>
						<td class="md-row sm-row"><span class="mobile-bold">${new_book.time}</span></td>
						<td class="md-row"><span class="mobile-only">Downloads: </span><a href="books/${new_book.id}/book.txt" target="_blank" download>Text</a></td>
						<td class="md-row"><a href="books/${new_book.id}/book.pdf" target="_blank">PDF</a></td>
						<td class="md-row"><a href="books/${new_book.id}/book.epub" target="_blank">EPUB</a></td>
						<td class="md-row"><a href="books/${new_book.id}/book.mp3" target="_blank" download>MP3</a></td>
						<td><audio class="book-playback" controls preload="none" src="books/${new_book.id}/book.mp3"></audio></td>
						<td id="status_${new_book.id}"><span class="current-scan">Currently being scanned</span></td>
					</tr>`

				document.getElementById("books").prepend(elem)
			} else {
				document.getElementById("status_" + new_book.id).innerHTML = '<span class="current-scan">Currently being scanned</span>'
			}
		})
		.catch(() => alert("An error has occurred. Could not start scanning."))
}

function stopScan() {
	fetch("system/scan/stop", {method: "POST"})
		.then((response) => {
			if (response.ok) {
				document.getElementById("scan-listen").classList.remove("inactive")
				document.getElementById("scan-only").classList.remove("inactive")
				for (let elem of document.getElementById("playback-controls").children)
					elem.classList.add("inactive")

				document.getElementById("stop-scan").classList.add("inactive")
				for (let elem of document.getElementsByClassName("continue-scan"))
					elem.classList.remove("inactive")

				const status = document.getElementById("scan-status")
				status.classList.add("status-idle")
				status.classList.remove("status-active")
				status.innerText = "Scanner idle"

				return response.json()
			} else {
				return Promise.reject()
			}
		})
		.then((book) => {
			document.getElementById("pages_" + book.id).innerHTML = `<span class="mobile-bold">${book.pages}</span><span class="mobile-only"> page${(book.pages == 1) ? "" : "s"}, scanned at </span>`
			document.getElementById("status_" + book.id).innerHTML = `<a class="continue-scan bold" onClick="scan(false, ${book.id})">Continue scanning <i class="fa-solid fa-book-open"></i></a>`
		})
		.catch(() => alert("An error has occurred. Scan could not be stopped."))
}

function setVolume(volume) {
	fetch("/system/setVolume/" + volume, {method: "POST"})
		.then((response) => response.text())
		.then((text) => document.getElementById("volume").value = text)
}

function volumeDown() {
	setVolume(Number(document.getElementById("volume").value) - 10)
}

function volumeUp() {
	setVolume(Number(document.getElementById("volume").value) + 10)
}

function togglePause() {
	fetch("/system/togglePause", {method: "POST"})
		.then((response) => response.text())
		.then((text) => {
			document.getElementById("playpause").innerHTML = `<i class="fa-solid ${(text === "False") ? "fa-play" : "fa-pause"}"></i>`
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
