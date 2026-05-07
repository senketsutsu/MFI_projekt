window.triggerConfetti = function () {
    if (window.confetti) {
        window.confetti({
            particleCount: 120,
            spread: 80,
            origin: { y: 0.6 }
        });
    }
};