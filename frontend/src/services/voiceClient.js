// Fetch token from localStorage
const accessToken = localStorage.getItem("access_token");

// Ensure we have a valid token before connecting
if (!accessToken) {
    alert("You must be logged in to join voice chat!");
    window.location.href = "/login.html";
}

// Connect WebSocket with Authorization
const ws = new WebSocket(`wss://yourserver.com/voice?token=${accessToken}`);

ws.onopen = () => {
    console.log("Connected to WebSocket server");
};

ws.onerror = (error) => {
    console.error("WebSocket error:", error);
};

// Example of sending API requests with Auth Header
async function fetchUserProfile() {
    try {
        const response = await fetch("/api/user/profile", {
            method: "GET",
            headers: { 
                "Authorization": `Bearer ${accessToken}`,
                "Content-Type": "application/json"
            }
        });

        const data = await response.json();
        console.log("User Profile:", data);
    } catch (error) {
        console.error("Error fetching profile:", error);
    }
}

// Call function when the script loads
fetchUserProfile();
