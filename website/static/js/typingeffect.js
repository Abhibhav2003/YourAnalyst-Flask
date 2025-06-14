    const texts = [
        "Welcome to YourAnalyst!",
        "Simplifying Data for You.",
        "Visualize. Analyze. Grow.",
        "Your data, your way."
    ];

    let count = 0;
    let index = 0;
    let currentText = '';
    let letter = '';

    function type() {
        if (count === texts.length) count = 0;
        currentText = texts[count];
        letter = currentText.slice(0, ++index);

        document.getElementById('typing-text').textContent = letter;

        if (letter.length === currentText.length) {
            setTimeout(() => {
                index = 0;
                count++;
                setTimeout(type, 400);
            }, 600);
        } else {
            setTimeout(type, 50);
        }
    }
window.onload = type;