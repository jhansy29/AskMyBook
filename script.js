const recordButton = document.getElementById('record');
const stopButton = document.getElementById('stop');
const audioElement = document.getElementById('audio');
const timerDisplay = document.getElementById('timer');

let mediaRecorder;
let audioChunks = [];
let startTime;
let timerInterval;

function formatTime(time) {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

recordButton.addEventListener('click', () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            audioChunks = [];
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            startTime = Date.now();
            timerInterval = setInterval(() => {
                const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
                timerDisplay.textContent = formatTime(elapsedTime);
            }, 1000);

            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

            mediaRecorder.onstop = () => {
                clearInterval(timerInterval);
                timerDisplay.textContent = '00:00';

                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                audioElement.src = audioUrl;

                const formData = new FormData();
                formData.append('file', audioBlob, 'recorded_audio.wav');

                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                    .then(response => {
                        if (!response.ok) {
                            console.error('Audio upload failed:', response.statusText);
                            throw new Error('Audio upload failed');
                        }
                        console.log('Audio uploaded successfully');
                        location.reload();
                    })
                    .catch(error => {
                        console.error('Error uploading audio:', error);
                    });
            };
        })
        .catch(error => {
            console.error('Error accessing microphone:', error);
        });

    recordButton.disabled = true;
    stopButton.disabled = false;
});

stopButton.addEventListener('click', () => {
    if (mediaRecorder) {
        mediaRecorder.stop();
    }
    recordButton.disabled = false;
    stopButton.disabled = true;
});