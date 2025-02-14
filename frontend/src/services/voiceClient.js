class VoiceClient {
    constructor(roomId, token) {
        this.roomId = roomId;
        this.token = token;
        this.ws = null;
        this.stream = null;
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.sourceNodes = new Map();
    }

    connect() {
        this.ws = new WebSocket(`ws://localhost:8000/voice/${this.roomId}?token=${this.token}`);

        this.ws.onopen = () => {
            console.log("🔊 Connected to voice server");
            this.startAudioCapture();
        };

        this.ws.onmessage = (event) => {
            this.handleIncomingAudio(event.data);
        };

        this.ws.onerror = (error) => {
            console.error("⚠️ WebSocket error:", error);
        };

        this.ws.onclose = () => {
            console.warn("❌ Disconnected from voice server");
            this.cleanup();
            setTimeout(() => this.connect(), 3000); // Auto-reconnect
        };
    }

    async startAudioCapture() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const audioTrack = this.stream.getAudioTracks()[0];
            const mediaRecorder = new MediaRecorder(this.stream);
            mediaRecorder.start(250); // Capture small audio chunks

            mediaRecorder.ondataavailable = (event) => {
                if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(event.data);
                }
            };

            console.log("🎤 Audio capture started");
        } catch (error) {
            console.error("⚠️ Error accessing microphone:", error);
        }
    }

    handleIncomingAudio(data) {
        const audioBlob = new Blob([data], { type: "audio/webm" });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.play();
    }

    cleanup() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
    }

    disconnect() {
        this.cleanup();
        console.log("🔇 Disconnected from voice chat");
    }
}

export default VoiceClient;
