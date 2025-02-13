const accessToken = localStorage.getItem("access_token");
if (!accessToken) {
    alert("Você deve estar logado para para acessar as voice rooms.");
    window.location.href = "/login.html";
}

const ws = new WebSocket(`ws://localhost:8000/ws/voice?token=${accessToken}`);

ws.onopen = () => {
    console.log("✅ Conectado ao servidor do WebSocket.");
};

ws.onerror = (error) => {
    console.error("❌ Erro no WebSocket:", error);
};

ws.onclose = () => {
    console.warn("⚠️ WebSocket fechato, tentando abrir novamente.");
    setTimeout(() => {
        location.reload();
    }, 5000);
};

async function fetchUserProfile() {
    try {
        const response = await fetch("/auth/me", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${accessToken}`,
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error("Não autorizado.");
        }

        const data = await response.json();
        console.log("✅ Perfil de usuário:", data);
    } catch (error) {
        console.error("❌ Erro ao pegar perfil:", error);
        window.location.href = "/login.html";
    }
}

fetchUserProfile();