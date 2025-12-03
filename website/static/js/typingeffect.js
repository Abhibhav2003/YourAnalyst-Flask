const texts = [
    "Welcome to YourAnalyst!",
    "Simplifying Data for You.",
    "Visualize. Analyze. Grow.",
    "Your data, your way."
];

let count = 0;
let index = 0;

function type() {
    if (count === texts.length) count = 0;
    let currentText = texts[count];

    document.getElementById("typing-text").textContent = currentText.slice(0, index);
    index++;

    if (index > currentText.length) {
        setTimeout(() => {
            index = 0;
            count++;
            type();
        }, 800);
    } else {
        setTimeout(type, 50);
    }
}

window.onload = type;