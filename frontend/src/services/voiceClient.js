const ws = new WebSocket("wss://yourserver.com/voice");

ws.onopen = () => {
    console.log("Connected to WebSocket server");
};

ws.onerror = (error) => {
    console.error("WebSocket error:", error);
};

async function fetchUserProfile() {
    try {
        const response = await fetch("/auth/me", {
            method: "GET",
            credentials: "include"  
        });

        if (!response.ok) {
            throw new Error("Unauthorized");
        }

        const data = await response.json();
        console.log("User Profile:", data);
    } catch (error) {
        console.error("Error fetching profile:", error);
        window.location.href = "/"; 
    }
}

fetchUserProfile();