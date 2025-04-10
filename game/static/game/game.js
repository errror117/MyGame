// static/game/game.js

document.addEventListener("DOMContentLoaded", function () {
    const startBtn = document.getElementById("start-game-btn");
    const attackBtn = document.getElementById("attack-btn");
    const collectItemBtn = document.getElementById("collect-item-btn");

    let sessionId = null;
    let health = 100;
    let score = 0;

    startBtn.addEventListener("click", function () {
        fetch("/game/start/", { method: "POST", headers: { "X-CSRFToken": getCSRFToken() } })
            .then(response => response.json())
            .then(data => {
                sessionId = data.session_id;
                alert("Game Started!");
                startBtn.disabled = true;
                attackBtn.disabled = false;
                collectItemBtn.disabled = false;
            });
    });

    attackBtn.addEventListener("click", function () {
        fetch("/game/enemy-attack/", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
            body: JSON.stringify({ session_id: sessionId })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            health = data.remaining_health;
            document.getElementById("health").innerText = health;

            if (health <= 0) {
                alert("Game Over!");
                attackBtn.disabled = true;
                collectItemBtn.disabled = true;
            }
        });
    });

    collectItemBtn.addEventListener("click", function () {
        fetch("/game/collect-item/", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
            body: JSON.stringify({ session_id: sessionId, item: "Health Potion" })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            document.getElementById("health").innerText = data.health;
        });
    });

    function getCSRFToken() {
        return document.cookie.split("; ")
            .find(row => row.startsWith("csrftoken"))
            ?.split("=")[1];
    }
});
