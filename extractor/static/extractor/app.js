const API_BASE = "http://127.0.0.1:8000/api";

const urlInput = document.getElementById("youtube-url");
const checkBtn = document.getElementById("check-btn");

const videoInfo = document.getElementById("video-info");
const videoTitle = document.getElementById("video-title");

const languageSection = document.getElementById("language-section");
const languageSelect = document.getElementById("language");

const extractBtn = document.getElementById("extract-btn");

const statusText = document.getElementById("status");

const result = document.getElementById("result");
const lyrics = document.getElementById("lyrics");
const downloadBtn = document.getElementById("download-btn");

let currentLrc = "";


// ==========================
// CHECK LANGUAGES
// ==========================

checkBtn.addEventListener("click", async () => {

    const url = urlInput.value.trim();

    if (!url) {
        setStatus("Masukkan URL YouTube.");
        return;
    }

    setStatus("Checking captions...");

    languageSection.classList.add("hidden");
    videoInfo.classList.add("hidden");
    result.classList.add("hidden");

    try {

        const response = await fetch(
            `${API_BASE}/languages/`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    url: url
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Failed to get captions."
            );
        }

        videoTitle.textContent = data.title;

        videoInfo.classList.remove("hidden");

        languageSelect.innerHTML = "";

        data.languages.forEach(language => {

            const option = document.createElement("option");

            option.value = language;
            option.textContent = language;

            languageSelect.appendChild(option);

        });

        languageSection.classList.remove("hidden");

        setStatus(
            `${data.languages.length} language(s) available.`
        );

    } catch (error) {

        setStatus(error.message);

    }

});


// ==========================
// EXTRACT LYRICS
// ==========================

extractBtn.addEventListener("click", async () => {

    const url = urlInput.value.trim();
    const language = languageSelect.value;

    if (!url || !language) {
        return;
    }

    setStatus("Extracting lyrics...");

    result.classList.add("hidden");

    try {

        const response = await fetch(
            `${API_BASE}/extract/`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    url: url,
                    language: language
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Failed to extract lyrics."
            );
        }

        currentLrc = data.lrc;

        lyrics.textContent = data.lrc;

        result.classList.remove("hidden");

        setStatus(
            `Lyrics extracted successfully (${data.language}).`
        );

    } catch (error) {

        setStatus(error.message);

    }

});


// ==========================
// DOWNLOAD LRC
// ==========================

downloadBtn.addEventListener("click", () => {

    if (!currentLrc) {
        return;
    }

    const blob = new Blob(
        [currentLrc],
        {
            type: "text/plain;charset=utf-8"
        }
    );

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download = "lyrics.lrc";

    link.click();

    URL.revokeObjectURL(url);

});


// ==========================
// STATUS
// ==========================

function setStatus(message) {
    statusText.textContent = message;
}