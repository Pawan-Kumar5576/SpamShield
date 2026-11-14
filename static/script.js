const messageBox = document.getElementById("message");
const counter = document.getElementById("counter");

if (messageBox && counter) {
  function updateCounter() {
    const length = messageBox.value.length;
    counter.textContent = `${length} / 10000 characters`;
    counter.style.color = length > 9000 ? "#c0392b" : "#8490a3";
  }
  messageBox.addEventListener("input", updateCounter);
  updateCounter();
}

console.log("SpamShield JavaScript loaded successfully.");