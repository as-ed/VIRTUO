let status = {}

function startStatusUpdates(scanning, listening, playing, paused, volume, num_books, current_book_pages, page_flip_error) {
	status = {
		scanning: scanning,
		listening: listening,
		playing: playing,
		paused: paused,
		volume: volume,
		num_books: num_books,
		current_book_pages: current_book_pages,
		page_flip_error: page_flip_error
	}

	if (scanning != null) {
		initCurrentAudio(playing, scanning)
	}

	setInterval(() => {
		fetch("system/status", {method: "GET"})
			.then((response) => response.json())
			.then((status) => updateStatus(status))
	}, 2000)
}

function updateStatus(newStatus) {
	if (newStatus.num_books != null && newStatus.num_books > document.getElementsByClassName("book").length) {
		status.num_books = newStatus

		fetch("books", {method: "GET"})
			.then((response) => response.json())
			.then((books) => {
				for (let book of books) {
					if (document.getElementById(book.id) == null) {
						const elem = document.createElement("tr")
						elem.id = book.id
						elem.classList.add("book")
						elem.innerHTML = `
							<td class="md-row sm-row"><input type="text" class="text-field" id="title_${book.id}" value="${book.title}" placeholder="Enter title" oninput="setTitle('${book.id}', this)" aria-label="title"></td>
							<td class="md-row sm-row"><input type="text" class="text-field" id="author_${book.id}" value="${book.author}" placeholder="Enter author" oninput="setAuthor('${book.id}', this)" aria-label="author"></td>
							<td id="pages_${book.id}" class="md-row sm-row"><span class="mobile-bold" aria-label="number of pages">${book.pages}</span><span class="mobile-only">  page${(book.pages === 1) ? "" : "s"}, scanned at </span></td>
							<td class="md-row sm-row"><span class="mobile-bold" aria-label="scanned at time">${book.time}</span></td>
							<td class="md-row"><span class="mobile-only">Downloads: </span><a href="books/${book.id}/book.txt" target="_blank" download aria-label="download text file">Text</a></td>
							<td class="md-row"><a href="books/${book.id}/book.pdf" target="_blank" aria-label="download PDF file">PDF</a></td>
							<td class="md-row"><a href="books/${book.id}/book.epub" target="_blank" aria-label="download EPUB file">EPUB</a></td>
							<td class="md-row"><a href="books/${book.id}/book.mp3" target="_blank" download aria-label="download MP3 file">MP3</a></td>
							<td><audio class="book-playback" controls preload="none" src="books/${book.id}/book.stream.mp3" aria-label="book playback"></audio></td>
							<td id="status_${book.id}" class="book-status">
							${(newStatus.scanning === book.id) ?
								'<span class="current-scan">Currently being scanned</span>'
							:
								`<a class="continue-scan bold ${(newStatus.scanning == null) ? "" : "inactive"}" onclick="scan(false, '${book.id}')" aria-label="continue scanning book">Continue scanning <i class="fa-solid fa-book-open"></i></a>`
							}
							</td>`

						document.getElementById("books").prepend(elem)
					}
				}

				setStatus(newStatus)
			})
	} else {
		setStatus(newStatus)
	}
}

function setStatus(newStatus) {
	if (status.scanning !== newStatus.scanning) {
		if (newStatus.scanning == null) {
			document.getElementById("scan-listen").classList.remove("inactive")
			document.getElementById("scan-only").classList.remove("inactive")

			document.getElementById("stop-scan").classList.add("inactive")
			for (let elem of document.getElementsByClassName("book-status"))
				elem.innerHTML = `<a class="continue-scan bold" onClick="scan(false, '${elem.id.substring(7)}')">Continue scanning <i class="fa-solid fa-book-open"></i></a>`

			const status = document.getElementById("scan-status")
			status.classList.add("status-idle")
			status.classList.remove("status-active")
			status.innerText = "Scanner idle"
		} else {
			const status = document.getElementById("scan-status")
			status.classList.remove("status-idle")
			status.classList.add("status-active")
			status.innerText = "Scanning in progress ..."

			document.getElementById("stop-scan").classList.remove("inactive")

			if (document.getElementById("status_" + newStatus.scanning))
				document.getElementById("status_" + newStatus.scanning).innerHTML = '<span class="current-scan">Currently being scanned</span>'
			for (let elem of document.getElementsByClassName("continue-scan"))
				elem.classList.add("inactive")
		}
	}

	if (newStatus.scanning != null && (status.scanning !== newStatus.scanning || status.listening !== newStatus.listening)) {
		if (newStatus.listening) {
			document.getElementById("scan-listen").classList.add("inactive")
			document.getElementById("scan-only").classList.remove("inactive")
		} else {
			document.getElementById("scan-listen").classList.remove("inactive")
			document.getElementById("scan-only").classList.add("inactive")
		}
	}

	if (status.playing !== newStatus.playing) {
		for (let elem of document.getElementById("playback-controls").children) {
			if (newStatus.playing) {
				elem.classList.remove("inactive")
			} else {
				elem.classList.add("inactive")
			}
		}

		initCurrentAudio(newStatus.playing, (newStatus.scanning == null) ? status.scanning : newStatus.scanning)
	}

	if (status.paused !== newStatus.paused)
		document.getElementById("playpause").innerHTML = `<i class="fa-solid ${newStatus.paused ? "fa-play" : "fa-pause"}"></i>`

	if (newStatus.volume != null && status.volume !== newStatus.volume) {
		status.volume = newStatus.volume
		document.getElementById("volume").value = status.volume
	}

	if (newStatus.current_book_pages >= 0 && status.current_book_pages !== newStatus.current_book_pages)
		document.getElementById("pages_" + newStatus.scanning).innerHTML = `<span class="mobile-bold">${newStatus.current_book_pages}</span><span class="mobile-only"> page${(newStatus.current_book_pages === 1) ? "" : "s"}, scanned at </span>`

	if (newStatus.page_flip_error != null && status.page_flip_error !== newStatus.page_flip_error) {
		const elem = document.getElementById("page-flip-error")

		if (newStatus.page_flip_error === 0) {
			elem.classList.add("hide-error")
		} else {
			elem.classList.remove("hide-error")
			document.getElementById("page-error-num-pages").innerText = newStatus.page_flip_error
		}
	}

	status.scanning = newStatus.scanning
	status.listening = newStatus.listening
	status.playing = newStatus.playing
	status.paused = newStatus.paused
	status.page_flip_error = newStatus.page_flip_error
}

function initCurrentAudio(playing, scanning) {
	if (playing) {
		const audio = document.getElementById(scanning).getElementsByTagName("audio")[0]
		audio.preload = "auto"
		audio.onplay = () => {
			fetch("/system/pause", {method: "POST"})
				.then(() => fetch("/system/playbackPos", {method: "GET"}))
				.then((response) => response.text())
				.then((pos) => {
					pos = parseFloat(pos)
					audio.currentTime = pos - 1
					while (this.currentTime < pos)
						this.currentTime = pos
				})
		}
		audio.onpause = () => {
			fetch(`/system/seek/${audio.currentTime - 1}`, {method: "POST"})
		}
	} else {
		const audio = document.getElementById(scanning).getElementsByTagName("audio")[0]
		audio.preload = "none"
		audio.onplay = null
		audio.onpause = null
	}
}

function scan(listen = false, book = null) {
	fetch("system/scan/start?listen=" + listen + ((book == null) ? "" : "&book=" + book), {method: "POST"})
		.then((response) => {
			if (response.ok) {
				return response.text()
			} else if (response.status === 400) {
				return Promise.reject(180)
			} else {
				return Promise.reject()
			}
		})
		.then((new_book) => {
			updateStatus({scanning: new_book, listening: listen, playing: false, paused: false, volume: null, num_books: null, current_book_pages: -1, page_flip_error: null})
		})
		.catch((err) => {
			console.log(err)

			if (err === 180)
				alert("It looks like the book is inserted upside down. Please rotate it 180 degrees around the vertical axis, clip it in and start the scan again.")
		})
}

function stopScan() {
	fetch("system/scan/stop", {method: "POST"})
		.then((response) => {
			if (response.ok) {
				updateStatus({scanning: null, listening: false, playing: false, paused: false, volume: null, num_books: null, current_book_pages: -1, page_flip_error: null})
			} else {
				alert("An error has occurred. Scan could not be stopped.")
			}
		})
}

function setVolume(volume) {
	status.volume = volume

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
	document.getElementById(status.scanning).getElementsByTagName("audio")[0].pause()

	fetch("/system/togglePause", {method: "POST"})
		.then((response) => response.text())
		.then((text) => {
			status.paused = text === "True"
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

function confirmManualFlip() {
	document.getElementById("page-flip-error").classList.add("hide-error")
	fetch("system/clearPageFlipError", {method: "POST"})
}

function openWifiSettings() {
	const elem = document.getElementById("wifi-settings")

	if (elem.classList.contains("hide-dialog"))
		elem.classList.remove("hide-dialog")
	else
		elem.classList.add("hide-dialog")
}

function closeWifiSettings() {
	document.getElementById("wifi-settings").classList.add("hide-dialog")
	document.getElementById("ssid").value = document.getElementById("password").value = ""
}

function addWifiNetwork() {
	const data = new FormData()
	data.append("ssid", document.getElementById("ssid").value)
	data.append("password", document.getElementById("password").value)
	fetch(`system/addWifi`, {method: "POST", body: data})

	closeWifiSettings()
}
