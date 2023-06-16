
// Show the "Generate sculpture" button when a file is selected
function showButton(input) {
    if (input.files && input.files[0]) {
        var button = document.getElementById("generateButton");
        button.style.display = "inline-block";
        button.style.marginBottom = "16px";
        button.style.top = "-50px";
        button.style.opacity = "0";
        var topPos = 0;
        var opacityVal = 0;
        var interval = setInterval(function() {
            if (topPos >= 50 && opacityVal >= 1) {
                clearInterval(interval);
            } else {
                topPos++;
                opacityVal += 0.02;
                button.style.top = -topPos + "px";
                button.style.opacity = opacityVal;
            }
        }, 10);
    }
}